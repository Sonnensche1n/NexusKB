<style lang="less">
.kb-app-debug {
  height: 100%;
  &-inputs {
    .notnull {
      position: relative;
    }
    .notnull::before {
      content: '*';
      color: var(--error-color);
      position: absolute;
      left: -12px;
      margin-top: 10px;
    }
  }
  .kb-chat-cont {
    border: 1px solid var(--border-color);
    .kb-chat-input {
      bottom: 10px;
    }
  }
}
</style>

<template>
  <n-message-provider>
    <n-flex class="kb-app-debug" vertical>
      <n-card class="kb-app-debug-inputs" title="输入变量" v-if="startNodeAttrs.length > 0">
        <p v-for="attr in startNodeAttrs" :key="`${attr.nodeId}-${attr.attrId}`" :class="attr.notNull === 'Y' ? 'notnull' : ''">
          <n-input v-if="attr.compTyp === 'textarea'" v-model:value="attr.attrVal" type="textarea" clearable :placeholder="`请输入${attr.attrLbl}`"></n-input>
          <n-select v-else-if="attr.compTyp === 'select'" v-model:value="attr.attrVal" :placeholder="`请选择${attr.attrLbl}`"
            :options="(attr['options'] || '').split(',').map(item => {
              return {
                label: item,
                value: item
              }
            })">
          </n-select>
          <n-input v-else v-model:value="attr.attrVal" type="input" :placeholder="`请输入${attr.attrLbl}`"></n-input>
        </p>
      </n-card>
      <content :reposId="appId" :chatId="appId" :on-send-message="onSendMessage" />
    </n-flex>
  </n-message-provider>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import useUserStore from '@/store/user'
  import { useDialog, useMessage } from 'naive-ui'
  import { isEmpty, deepCopy, uuid } from '@/libs/tools'
  import Content from '@/views/main/chat/Content.vue'

  export default defineComponent({
    components: {
      Content
    },
    props: {
      appId: String,
      graph: Object
    },
    setup(props) {
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      let graph = props.graph
      let appId = props.appId
      let nodes = graph.getNodes()
      let edges = graph.getEdges()
      let nodeDatas = nodes.map(node => node.data)
      let edgeDatas = edges.map(edge => edge.data)

      let startNodeAttrs = ref(deepCopy(nodeDatas.find(node => node.ndfId === 'start')?.attrs?.filter(attr => attr['builtIn'] !== 'Y' && attr['attrCls'] === 'ipt')))
      const onSendMessage = (mesg, messageList) => {
        mesg.mesgId = uuid()
        let fs = startNodeAttrs.value.filter(attr => isEmpty(attr.attrVal) && attr.notNull === 'Y')
        if (fs.length > 0) {
          message.error(`请输入必填项：${fs.map(attr => attr.attrLbl).join(',')}`)
          return
        }
        messageList.value.push(mesg)
        let inputs = {}
        startNodeAttrs.value.forEach(attr => {
          inputs[attr.attrId] = attr.attrVal
        })
        debug(mesg, inputs, messageList)
      }
      const debug = async (mesg, inputs, messageList) => {
        if (nodes.length == 0) {
          return message.error('请添加节点')
        }
        let childMesg = ref({
          mesgId: uuid(),
          mesgPid: mesg.mesgId,
          mesgCntnt: '',
          chatId: appId,
          mesgTyp: 'text',
          crtRole: 'sys'
        })
        messageList.value.push(childMesg.value)
        let params = { questions: [mesg.mesgCntnt], inputs, nodes: nodeDatas, edges: edgeDatas }
        proxy.$api.fetch(`/agt/app/flow/debug/${appId}`, params, message => {
          if (message === undefined) {
            childMesg.value.mesgCntnt = ' '
            return
          }
          // {"type": "chat_message_content", "data": "{\"result\": \"根据已知信息无法回答该问题，因为背景知识中未包含关于“xxx”的相关信息。\"}"}
          if (isEmpty(message)) {
            return
          }
          try {
            message = JSON.parse(message)
            if (message.type === 'chat_message_content') {
              let data = message.data || {}
              let keys = Object.keys(data)
              if (keys.length === 1) {
                let cntnt = data[keys[0]]
                cntnt = typeof cntnt === 'string' ? cntnt : JSON.stringify(cntnt)
                childMesg.value.mesgCntnt = cntnt
              } else {
                keys.forEach(key => {
                  let cntnt = data[key]
                  cntnt = typeof cntnt === 'string' ? cntnt : JSON.stringify(cntnt)
                  childMesg.value.mesgCntnt += '\n-----' + key + '-----\n' + cntnt + '\n'
                })
              }
            }
          } catch (error) {
            console.error(error)
            childMesg.value.mesgCntnt = message
          }
        })
      }
      return {
        startNodeAttrs,
        debug, onSendMessage
      }
    }
  })
</script>
