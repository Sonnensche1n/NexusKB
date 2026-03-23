<style lang="less">
.kb-chat.n-card > .n-card__content {
  padding: 0;
  overflow: hidden;
}
.kb-chat {
  height: 100%;
  .n-layout {
    height: 100%;
  }
  &-info {
    padding-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    .n-icon {
      font-size: 22px;
      margin-right: 4px;
      color: var(--primary-color);
    }
    .n-icon:last-child {
      color: var(--text-color-3);
      font-size: 14px;
    }
  }
  &-option {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    .n-button:nth-child(2) {
      width: 136px;
    }
  }
  &-list.n-list {
    margin-top: 20px;
    .n-list-item {
      position: relative;
      padding: 10px;
      margin-bottom: 6px;
      cursor: pointer;
      .n-list-item__main {
        width: calc(100% - 26px);
        .n-thing, .n-thing-main {
          width: 100%;
          .n-icon {
            margin-right: 4px;
            position: relative;
            top: 1px;
          }
        }
      }
      .n-list-item__suffix {
        visibility: hidden;
        margin-left: 0;
      }
      &:hover {
        .n-list-item__suffix {
          visibility: visible;
        }
        &::before {
          content: '';
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: -1px;
          border-radius: var(--border-radius);
          background-color: var(--border-color);
          opacity: 0.1;
        }
      }
    }
    .selected.n-list-item {
      .n-thing-main__content {
        color: var(--primary-color);
      }
      &::before {
        content: '';
        width: 100%;
        height: 100%;
        position: absolute;
        left: 0;
        top: -1px;
        border-radius: var(--border-radius);
        background-color: var(--primary-color);
        opacity: 0.1;
      }
    }
  }
}
</style>

<template>
  <n-card class="kb-chat" :bordered="false">
    <n-layout has-sider>
      <n-layout-sider bordered content-style="padding: 24px;">
        <div class="kb-chat-info">
          <n-icon class="iconfont-kb icon-knowledge"></n-icon>
          <n-dropdown trigger="hover" :options="reposOptions" :on-select="onReposSelect">
            <span title="切换对话知识库">{{ selectedRepos.reposNm }}</span>
          </n-dropdown>
          <n-icon class="iconfont icon-unfoldmore"></n-icon>
        </div>
        <div class="kb-chat-option">
          <n-button circle @click="turnToRepos" title="知识库详情"><n-icon class="iconfont icon-undovariant"></n-icon></n-button>
          <n-button round @click="addChat">
            <template #icon>
              <n-icon class="iconfont-kb icon-chat-add"></n-icon>
            </template>
            新对话
          </n-button>
          <n-button circle @click="clearChat" title="清空对话"><n-icon class="iconfont icon-broom"></n-icon></n-button>
        </div>
        <n-list class="kb-chat-list" :show-divider="false">
          <n-list-item v-for="chat in chatList" :key="chat.chatId" @click="onChatSelect(chat.chatId)" :class="selectedChatId === chat.chatId ? 'selected' : ''">
            <template #suffix>
              <n-dropdown :options="chatOptions" :on-select="(key) => {
                this.onChatOptionSelect(key, chat)
              }">
                <n-button size="tiny"><n-icon class="iconfont icon-dotshorizontal"></n-icon></n-button>
              </n-dropdown>
            </template>
            <n-thing>
              <n-ellipsis>
                <n-icon class="iconfont-kb icon-chat1"></n-icon>{{ chat.chatTtl }}
              </n-ellipsis>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-if="chatList.length === 0"/>
      </n-layout-sider>
      <n-layout-content content-style="padding: 24px;">
        <keep-alive>
          <Content :reposId="selectedReposId" :chatId="selectedChatId" :key="selectedChatId" v-if="selectedChatId" @on-send-first-message="onSendFirstMessage" />
        </keep-alive>
      </n-layout-content>
    </n-layout>
  </n-card>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { NCard, NLayout, NLayoutSider, NLayoutContent, NMenu, NButton, NIcon, NList, NListItem, NThing, NEllipsis, NDropdown, useDialog, useMessage } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { localRead, localSave } from '@/libs/tools'
  import { CURRENT_REPOS_ID_KEY } from '@/libs/enum'
  import Content from './chat/Content.vue'
  import ChatForm from './chat/form/ChatForm.vue'

  export default defineComponent({
    components: {
      NCard, NLayout, NLayoutSider, NLayoutContent, NMenu, NButton, NIcon, NList, NListItem, NThing, NEllipsis, NDropdown,
      Content
    },
    setup() {
      const dialog = useDialog()
      const message = useMessage()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const selectedReposId = ref('')
      const selectedChatId = ref('')
      const reposList = ref([])
      const chatList = ref([])
      const selectedRepos = computed(() => {
        return reposList.value.find(repos => repos.reposId === selectedReposId.value) || {}
      })
      const reposOptions = computed(() => {
        let list = []
        reposList.value.forEach(repos => {
          list.push({
            label: repos.reposNm,
            key: repos.reposId,
            icon: () => renderIconfontIcon('iconfont-kb icon-knowledge')
          },)
        })
        return list
      })
      const initChatList = (reposId) => {
        proxy.$api.post('/knb/chat/my/list', { reposId }).then(res => {
          chatList.value = res.data || []
          if (chatList.value.length > 0) {
            selectedChatId.value = chatList.value[0].chatId
          } else {
            selectedChatId.value = ''
          }
        }).catch(err => {
          console.error(err)
        })
      }
      const initReposList = () => {
        proxy.$api.post('/knb/repository/my/list').then(res => {
          reposList.value = res.data || []
          if (reposList.value.length > 0) {
            let currentId = localRead(CURRENT_REPOS_ID_KEY) || ''
            if (currentId) {
              let fs = reposList.value.filter(repos => repos.reposId === currentId)
              if (fs.length > 0) {
                selectedReposId.value = currentId
                return
              }
            }
            selectedReposId.value = reposList.value[0].reposId
          } else {
            selectedReposId.value = ''
            dialogConfirm(dialog, {
              title: '创建知识库确认',
              content: '您还没有创建知识库，是否去创建一个知识库？',
              type: 'warning',
              onPositiveClick: (e, dialog) => {
                router.push(`/main/repository`)
              }
            })
          }
        }).catch(err => {
          console.error(err)
        })
      }
      initReposList()
      const onChatSelect = (chatId) => {
        selectedChatId.value = chatId
      }
      const addChat = () => {
        if (reposList.value.length === 0) {
          message.error('请先创建知识库')
          dialogConfirm(dialog, {
            title: '创建知识库确认',
            content: '您还没有创建知识库，是否去创建一个知识库？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              router.push(`/main/repository`)
            }
          })
          return
        }
        proxy.$api.post('/knb/chat', { reposId: selectedReposId.value, chatTtl: '新对话' }).then(res => {
          // initChatList(selectedReposId.value)
          chatList.value.unshift(res.data)
          selectedChatId.value = res.data.chatId
        }).catch(err => {
          console.error(err)
        })
        /*
        dialogCreate(dialog, {
          title: `新增对话`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-chat-add', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            data.reposId = selectedReposId.value
            proxy.$api.post('/knb/chat', data).then(res => {
              initChatList(selectedReposId.value)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
            })
          }
        }, ChatForm, {
        })
        */
      }
      const clearChat = () => {
        dialogConfirm(dialog, {
          title: '确认',
          content: '确认清空知识库下的对话记录？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/knb/repository/chat/clear/' + selectedReposId.value).then(res => {
              initChatList(selectedReposId.value)
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }
      const chatOptions = [
        {
          label: '编辑',
          key: 'edit',
          icon: () => renderIconfontIcon('iconfont icon-pencil')
        },
        {
          label: '删除',
          key: 'delete',
          icon: () => renderIconfontIcon('iconfont icon-delete')
        }
      ]
      const onChatOptionSelect = (key, chat) => {
        if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改对话`,
            style: 'width: 40%;',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-chat1', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/knb/chat', data).then(res => {
                // initChatList(selectedReposId.value)
                chat.chatTtl = data.chatTtl
              }).catch(err => {
                console.error(err)
              })
              dialog.destroy()
            }
          }, ChatForm, {
            chat
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该对话么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/knb/chat/' + chat.chatId).then(res => {
                initChatList(selectedReposId.value)
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
              return false
            }
          })
        }
      }
      const onReposSelect = (key) => {
        selectedReposId.value = key
        localSave(CURRENT_REPOS_ID_KEY, key)
      }
      watch(selectedReposId,(newId, oldId)=>{
        initChatList(newId)
      })
      const router = useRouter()
      const turnToRepos = () => {
        router.push(`/main/repository/detail?id=${selectedReposId.value}`)
      }
      const onSendFirstMessage = (message) => {
        let chat = chatList.value.find(chat => chat.chatId === selectedChatId.value)
        if (chat && chat.chatTtl === '新对话') {
          chat.chatTtl = message
          proxy.$api.put('/knb/chat', chat).then(res => {
          }).catch(err => {
            console.error(err)
          })
        }
      }
      return {
        selectedRepos,
        reposOptions,
        chatOptions,
        chatList, selectedChatId, selectedReposId,
        onChatSelect, addChat, clearChat, onChatOptionSelect, onReposSelect, turnToRepos, onSendFirstMessage
      }
    }
  })
</script>
