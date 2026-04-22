<style lang="less">
.kb-chat-cont {
  height: 100%;
  position: relative;
  .kb-chat-message {
    height: calc(100% - 80px);
    overflow: auto;
    .n-scrollbar-container .n-scrollbar-content {
      padding-bottom: 10px;
    }
  }
  .kb-chat-input {
    position: absolute;
    width: 70%;
    left: 15%;
    bottom: 0;
    .n-input {
      min-height: 60px;
      padding-top: 9px;
      padding-bottom: 9px;
    }
    .n-button {
      position: absolute;
      bottom: 13px;
      right: 13px;
    }
  }
}
</style>

<template>
  <div class="kb-chat-cont">
    <n-scrollbar :id="`c${chatId}`" ref="scrollbarRef" class="kb-chat-message">
      <message v-for="mesg in messageList" :key="mesg.mesgId" :message="mesg" @on-delete-message="onDeleteMessage" @on-regen-message="onRegenMessage" />
      <guess-quest v-if="guessQuestList.length > 0" :quest-list="guessQuestList" @on-quest-change="onQuestChange" />
      <n-back-top :to="`#c${chatId}`" :right="24" :bottom="32" />
    </n-scrollbar>
    <div class="kb-chat-input">
      <n-input v-model:value="inputValue" autofocus placeholder="输入问题，发送 [Enter]/换行 [Ctrl + Enter]" type="textarea" size="large" :on-input="onInputChange" @keydown="onInputKeyDown"
        :autosize="{
          minRows: 1,
          maxRows: 5
        }"
      />
      <n-button @click="sendMessage" :disabled="!Boolean(inputValue)" type="primary" circle><n-icon class="iconfont icon-send"></n-icon></n-button>
    </div>
  </div>
</template>
<script>
  import { defineComponent, ref, nextTick, getCurrentInstance, computed } from 'vue'
  import _ from 'lodash'
  import Message from './Message.vue'
  import { random, isEmpty } from '@/libs/tools'
  import EventBus from '@/libs/eventbus'
  import GuessQuest from './GuessQuest.vue'
  export default defineComponent({
    components: {
      Message, GuessQuest
    },
    props: [ 'chatId', 'reposId', 'on-send-message' ],
    setup(props, context) {
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const reposId = props.reposId
      const chatId = props.chatId
      const scrollbarRef = ref()
      const inputValue = ref('')
      const messageList = ref([])
      const lastMessage = computed(() => {
        if (messageList.value.length === 0) return {
          value: {}
        }
        return messageList.value[messageList.value.length - 1]
      })
      const create_new_message = (message = {}) => {
        return { mesgId: '', reposId, chatId, mesgPid: '', mesgCntnt: '', mesgTyp: 'text', crtUser: '',
          crtRole: 'sys', // sys, usr
          crtTm: null,
          ...message
        }
      }
      const initMessageList = () => {
        proxy.$api.post('/knb/chat/message/list', { chatId }).then(res => {
          messageList.value = res.data || []
          scrollToBottom()
          if (messageList.value.length === 0) {
            initQuessQuestList()
            messageList.value.push(create_new_message({
              mesgCntnt: '您好，我是NexusKB，有什么可以帮到您？',
              mesgTyp: 'text',
              crtRole: 'sys',
            }))
          }
        }).catch(err => {
          console.error(err)
        })
      }
      initMessageList()
      const scrollToBottom = _.debounce(() => {
        nextTick(() => {
          scrollbarRef.value?.scrollTo({
            top: 999999
          })
        })
      }, 10)
      const onSendMessage = props['on-send-message'] || props['onSendMessage']
      const sendMessage = () => {
        if (isEmpty(inputValue.value)) {
          return
        }
        let mesg = create_new_message({
          mesgCntnt: inputValue.value,
          mesgTyp: 'text',
          crtRole: 'usr',
        })
        if (onSendMessage) {
          onSendMessage(mesg, messageList)
        } else {
          if (messageList.value.filter(m => m.crtRole === 'usr').length === 0) {
            context.emit('on-send-first-message', inputValue.value)
          }
          let history = messageList.value.slice(-20) // 默认20条历史数据，后台根据配置截取
          messageList.value.push(mesg)
          let childMesg = ref(create_new_message({
            mesgTyp: 'text',
            crtRole: 'sys', // sys, usr
            crtTm: null,
            quotes: []
          }))
          messageList.value.push(childMesg.value)
          proxy.$api.fetch('/knb/chat/message', { mesg, history }, event => {
            handleMessageEvent(mesg, childMesg, event, true)
          })
        }
        inputValue.value = ''
        scrollToBottom()
      }

      const onInputKeyDown = (e) => {
        let keyCode = e.keyCode
        if (keyCode === 13) { // enter
          if (!e.ctrlKey) {
            e.preventDefault()
            sendMessage()
          } else {
            inputValue.value += '\n'
          }
        }
      }

      const guessQuestList = ref([])
      const initQuessQuestList = (value) => {
        if (onSendMessage) {
          return
        }
        proxy.$api.post('/knb/repository/guess/list', { reposId, qstQuest: value }).then(res => {
          guessQuestList.value = res.data || []
          nextTick(() => scrollToBottom())
        }).catch(err => {
          console.error(err)
        })
      }
      const onInputChange = _.debounce((value) => {
        if (isEmpty(value)) {
          value = null
        }
        initQuessQuestList(value)
      }, 500)

      const onQuestChange = (text) => {
        inputValue.value = text
        sendMessage()
        guessQuestList.value = []
      }

      const onDeleteMessage = (mesgId) => {
        proxy.$api.delete('/knb/chat/message/' + mesgId).then(res => {
          messageList.value = messageList.value.filter(mesg => mesg.mesgId !== mesgId && mesg.mesgPid !== mesgId)
          if (messageList.value.length === 0) {
            initQuessQuestList()
          }
        }).catch(err => {
          console.error(err)
        })
      }

      const onRegenMessage = (message) => {
        // 找到该消息之前的6条历史记录
        let i = messageList.value.findIndex(mesg => mesg.mesgId === message.mesgId)
        let history = messageList.value.slice(Math.max(0, i - 10), i) // 默认6条历史数据
        let childMesg = messageList.value.find(mesg => mesg.mesgPid === message.mesgId)
        let isNewChild = false
        if (!childMesg) {
          childMesg = ref(create_new_message({
            mesgTyp: 'text',
            crtRole: 'sys', // sys, usr
            crtTm: null,
            quotes: []
          }))
          messageList.value.splice(i + 1, 0, childMesg.value)
          isNewChild = true
        } else {
          childMesg = ref(childMesg)
        }
        childMesg.value.mesgCntnt = ''
        proxy.$api.fetch('/knb/chat/remessage', { mesg: message, history }, event => {
          handleMessageEvent(message, childMesg, event, isNewChild)
        })
      }
      const handleMessageEvent = (parentMesg, childMesg, event, isNewChild) => {
        if (isEmpty(event)) {
          return
        }
        try {
          let message = {}
          try {
            message = JSON.parse(event)
          } catch (e) {
            console.error(e)
            // 后端 SSE 事件应为严格 JSON；禁止 eval 以避免安全风险
            return
          }
          
          let type = message.type || ''
          if (type === 'chat_message_entity') {
            let data = message.data || {}
            if (isNewChild) {
              childMesg.value.mesgId = data.mesgId
              childMesg.value.mesgPid = data.mesgPid
              childMesg.value.crtTm = data.crtTm
            }
            if (!parentMesg.mesgId) {
              parentMesg.mesgId = data.mesgPid
            }
          } else if (type === 'chat_message_chunk') {
            let data = message.data || ''
            if (data) {
              childMesg.value.mesgCntnt += data
              if (lastMessage.value.mesgId === childMesg.value.mesgId) {
                scrollToBottom()
              }
            }
          } else if (type === 'chat_message_quote') {
            childMesg.value['quotes'] = message.data['quotes']
            childMesg.value['toolStatus'] = ''
          } else if (type === 'chat_tool_call') {
            let data = message.data || {}
            let tool = data.tool || 'tool'
            let status = data.status || ''
            if (status === 'running') {
              childMesg.value['toolStatus'] = `正在调用 ${tool}...`
            } else if (status === 'done') {
              childMesg.value['toolStatus'] = `${tool} 已完成`
            } else {
              childMesg.value['toolStatus'] = ''
            }
          } else if (type === 'chat_message_error') {
            childMesg.value['error'] = message.data || '未知错误，暂时无法回答'
            childMesg.value['toolStatus'] = ''
          }
        } catch (error) {
          console.error(error)
        }
      }

      return {
        scrollbarRef,
        inputValue, messageList, guessQuestList,
        sendMessage, onInputKeyDown, onInputChange, onQuestChange, onDeleteMessage, onRegenMessage
      }
    }
  })
</script>
