<style lang="less">
.kb-chat-mesg {
  display: flex;
  flex-grow: 0;
  flex-direction: row;
  gap: 5px;
  padding: 20px;
  position: relative;
  &-avatar {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    line-height: 36px;
    border-radius: 50%;
    text-align: center;
    .n-icon {
      color: #FFFFFF;
      font-size: 20px;
      line-height: 36px;
    }
  }
  &-content {
    padding: 7px;
    border-radius: 5px;
    overflow: auto;
    .thinking {
      @keyframes text-up-down {
        0% {
          transform: translateY(0px);
        }
        20% {
          transform: translateY(-6px);
        }
        40%, 100% {
          transform: translateY(0px);
        }
      }
      span {
        display: inline-block;
        animation: text-up-down 1.5s ease-in-out infinite;
        animation-delay: calc(.1s*var(--i));
      }
    }
    .quote {
      .n-divider {
        margin: 5px 0;
      }
      .n-divider__title {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-color-3);
        .icon-quote.n-icon {
          color: var(--warning-color);
          font-size: 24px;
          margin-right: 4px;
        }
      }
      .n-tag {
        cursor: pointer;
        &:hover {
          background-color: var(--primary-color-opacity-4)
        }
      }
    }
  }
  &-error {
    line-height: 36px;
    cursor: pointer;
    .n-icon {
      color: var(--error-color);
    }
    &:hover {
      .n-icon {
        color: var(--error-color-hover);
      }
    }
  }
  &-option {
    position: absolute;
    bottom: -10px;
    visibility: hidden;
    z-index: 1;
    .ivu-icon {
      font-size: 16px;
      cursor: pointer;
      color: #C2C2C2;
    }
    .delete.n-button {
      color: var(--error-color);
      &:hover {
        color: var(--error-color-hover);
      }
    }
  }
  &:hover {
    .kb-chat-mesg-option {
      visibility: visible;
    }
  }
}
.kb-chat-mesg-sys {
  .kb-chat-mesg-avatar {
    background-color: var(--primary-color);
  }
  .kb-chat-mesg-option {
    left: 63px;
  }
  .kb-chat-mesg-content {
    background-color: var(--code-color);
  }
}
.kb-chat-mesg-usr {
  flex-direction: row-reverse;
  .kb-chat-mesg-avatar {
    background-color: var(--primary-color);
  }
  .kb-chat-mesg-option {
    right: 63px;
  }
  .kb-chat-mesg-content {
    background-color: var(--primary-color);
    color: #fff;
  }
}
</style>

<template>
  <div :class="[ 'kb-chat-mesg', `kb-chat-mesg-${message.crtRole}` ]">
    <div class="kb-chat-mesg-avatar">
      <n-icon v-if="message.crtRole === 'usr'" class="iconfont-kb icon-user" />
      <n-icon v-else :class="`iconfont-kb icon-ai${ thinking ? 2 : 1 }`" />
    </div>
    <div class="kb-chat-mesg-option">
      <n-button-group size="tiny">
        <n-button class="copy" ghost @click="copyToClipboard" title="复制"><n-icon class="iconfont-kb icon-copy-fill"></n-icon></n-button>
        <n-button class="speakoff" v-if="speaking"  ghost @click="speakOff" title="关闭朗读"><n-icon class="iconfont icon-volumeoff"></n-icon></n-button>
        <n-button class="speakon" v-else ghost @click="speakOn" title="朗读"><n-icon class="iconfont icon-volumehigh"></n-icon></n-button>
        <n-button class="regen" v-if="message.crtRole === 'usr'" ghost @click="regenMessage" title="重新生成"><n-icon class="iconfont icon-refresh"></n-icon></n-button>
        <n-button class="edit" ghost @click="editMessage" title="编辑"><n-icon class="iconfont icon-pencilboxoutline"></n-icon></n-button>
        <n-button class="delete" v-if="message.crtRole === 'usr'" ghost @click="deleteMessage" title="删除"><n-icon class="iconfont icon-delete"></n-icon></n-button>
      </n-button-group>
    </div>
    <div class="kb-chat-mesg-content">
      <p class="thinking" v-if="thinking">
        <span style="--i:1">正</span>
        <span style="--i:2">在</span>
        <span style="--i:3">思</span>
        <span style="--i:4">考</span>
        <span style="--i:5">中</span>
        <span style="--i:6">·</span>
        <span style="--i:7">·</span>
        <span style="--i:8">·</span>
      </p>
      <template v-else>
        <div v-if="message.crtRole === 'usr'" v-html="message.mesgCntnt?.replace(/\n+/g, '<br>')"></div>
        <message-view v-else :content="message.mesgCntnt" />
        <div class="quote" v-if="(message['quotes'] || []).length > 0">
          <n-divider title-placement="left">
            <n-icon class="iconfont-kb icon-quote" />引用
          </n-divider>
          <n-space size="small" @click="onQuoteClick">
            <n-tag :bordered="false" v-for="(file, index) in quoteFiles.splice(0, 5)" :key="`${message.mesgId}-${file}-${index}`" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
              {{ file }}
              <template #icon>
                <n-icon class="iconfont icon-file" />
              </template>
            </n-tag>
          </n-space>
        </div>
        <div class="guess" v-if="(message['guesses'] || []).length > 0">
          <n-divider title-placement="left">
            <n-icon class="iconfont-kb icon-quote" />推荐
          </n-divider>
          <n-space size="small">
            <n-tag :bordered="false" v-for="(file, index) in quoteFiles" :key="`${message.mesgId}-${file}-${index}`" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
              {{ file }}
              <template #icon>
                <n-icon class="iconfont icon-file" />
              </template>
            </n-tag>
          </n-space>
        </div>
      </template>
    </div>
    <n-tooltip v-if="error" trigger="hover" :style="{ maxWidth: '300px' }">
      <template #trigger>
        <div class="kb-chat-mesg-error">
          <n-icon class="iconfont icon-alert"/>
        </div>
      </template>
      {{ error }}
    </n-tooltip>
  </div>
</template>
<script>
  import { defineComponent, computed, ref, onBeforeUnmount, getCurrentInstance } from 'vue'
  import { useMessage, useDialog } from 'naive-ui'
  import { isEmpty } from '@/libs/tools'
  import { renderIconfontIcon, dialogCreate } from '@/libs/utils'
  import MessageView from './message/MessageView.vue'
  import MessageQuotes from './MessageQuotes.vue'
  import MessageForm from './form/MessageForm.vue'
  import EventBus from '@/libs/eventbus'

  export default defineComponent({
    components: {
      MessageView
    },
    props: {
      message: {
        type: Object,
        required: true
      },
    },
    setup(props, context) {
      const { proxy, ctx } = getCurrentInstance()
      const dialog = useDialog()
      const message = useMessage()
      const quoteFiles = computed(() => {
        let files = []
        if (props.message.quotes && props.message.quotes.length > 0) {
          props.message.quotes.forEach(quote => {
            let nm = quote.dtsetNm + '.' + quote.fileTyp
            if (!files.includes(nm)) {
              files.push(nm)
            }
          })
        }
        return files
      })
      const thinking = computed(() => {
        return Boolean(props.message['thinking']) || isEmpty(props.message.mesgCntnt)
      })
      const error = computed(() => {
        return props.message['error']
      })
      const copyToClipboard = async () => {
        try {
          await navigator.clipboard.writeText(props.message.mesgCntnt?.replace(/<br>/g, '\n'))
          message.success('复制成功')
        } catch (err) {
          console.error('复制失败', err);
        }
      }
      const deleteMessage = () => {
        context.emit('on-delete-message', props.message.mesgId)
      }
      const regenMessage = () => {
        context.emit('on-regen-message', props.message)
      }

      const editMessage = () => {
        dialogCreate(dialog, {
          title: `修改消息`,
          style: 'width: 60%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont icon-messagedraw', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.put('/knb/chat/message', data).then(res => {
              props.message.mesgCntnt = data.mesgCntnt
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, MessageForm, {
          message: props.message
        })
      }

      const speaking = ref(false)
      const speakOff = () => {
        EventBus.emit('on-speech-off')
        speaking.value = false
      }
      const speakOn = () => {
        EventBus.emit('on-speech-on', props.message.mesgCntnt)
        speaking.value = true
      }
      
      const onSpeechEnd = () => {
        speaking.value = false
      }

      const onQuoteClick = () => {
        dialogCreate(dialog, {
          title: `引用查看`,
          style: 'width: 60%;',
          negativeText: '',
          positiveText: '',
          icon: () => renderIconfontIcon('iconfont-kb icon-quote', { size: '28px' })
        }, MessageQuotes, {
          quoteList: props.message.quotes
        })
      }

      EventBus.on('on-speech-onend', onSpeechEnd)
      onBeforeUnmount(() => {
        EventBus.off('on-speech-onend', onSpeechEnd)
      })

      return {
        quoteFiles, thinking, error, speaking,
        copyToClipboard, deleteMessage, speakOn, speakOff, regenMessage, editMessage, onQuoteClick
      }
    }
  })
</script>
