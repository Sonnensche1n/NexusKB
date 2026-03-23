<style lang="less">
</style>

<template>
  <n-collapse class="kb-flow-node-content" :default-expanded-names="defaultExpandedNames" :on-update:expanded-names="onUpdateExpandedNames" :trigger-areas="[]">
    <template #arrow>
      <i></i>
    </template>
    <n-collapse-item title="输入" name="input" v-if="!(inputAttrs.length === 0 && nodeData.nodeDef?.addInput !== 'Y')">
      <template #header-extra v-if="nodeData.nodeDef?.addInput === 'Y'">
        <n-button text size="small" title="添加变量" @click="addInputAttr">
          <n-icon class="iconfont icon-plus" />
        </n-button>
      </template>
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item v-for="attr in inputAttrs" :key="`${attr.nodeId}-${attr.attrId}`" :class="attr.notNull === 'Y' ? 'notnull' : ''">
          <attr-view :attr="attr" v-if="attr.valSrc === 'aut'" />
          <attr-input v-else :attr="attr" />
          <template #suffix v-if="attr.builtIn !== 'Y'">
            <n-button size="small" text type="error" title="删除">
              <n-icon class="iconfont icon-delete" @click="removeAttr(attr.attrId)" />
            </n-button>
          </template>
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <div class="kb-flow-node-other" v-if="otherAttrs.length > 0">
      <n-collapse-item :title="attr.attrLbl" :name="attr.attrKey" v-for="attr in otherAttrs" :key="`${attr.nodeId}-${attr.attrId}`">
        <n-list class="kb-var-list" :show-divider="false">
          <n-list-item :class="attr.notNull === 'Y' ? 'notnull' : ''">
            <attr-view :attr="attr" v-if="attr.valSrc === 'aut'" />
            <attr-input v-else :attr="attr" />
          </n-list-item>
        </n-list>
      </n-collapse-item>
    </div>
    <n-collapse-item title="输出" name="output" v-if="!(outputAttrs.length === 0 && nodeData.nodeDef?.addOutput !== 'Y')">
      <template #header-extra v-if="nodeData.nodeDef?.addOutput === 'Y'">
        <n-button text size="small" title="添加变量" @click="addOutputAttr">
          <n-icon class="iconfont icon-plus" />
        </n-button>
      </template>
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item v-for="attr in outputAttrs" :key="`${attr.nodeId}-${attr.attrId}`" :class="attr.notNull === 'Y' ? 'notnull' : ''">
          <attr-view :attr="attr" v-if="attr.valSrc === 'aut'" />
          <attr-input v-else :attr="attr" />
          <template #suffix v-if="attr.builtIn !== 'Y'">
            <n-button size="small" text type="error" title="删除">
              <n-icon class="iconfont icon-delete" @click="removeAttr(attr.attrId)" />
            </n-button>
          </template>
        </n-list-item>
      </n-list>
    </n-collapse-item>
  </n-collapse>
</template>
<script>
  import { defineComponent, ref, computed, watch, onMounted } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { uuid, isEmpty } from '@/libs/tools'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { useNode } from '../mixin/node'
  import AttrInput from './components/AttrInput.vue'
  import AttrView from './components/AttrView.vue'
  import AddInputAttrForm from './components/form/AddInputAttrForm.vue'
  
  export default defineComponent({
    components: {
      AttrInput, AttrView
    },
    setup(props, context) {
      const dialog = useDialog()
      const { nodeData, resizeNode } = useNode()
      const appId = nodeData['appId']
      const attrs = ref(nodeData['attrs'] || [])
      const inputAttrs = computed(() => attrs.value.filter(item => item.attrCls === 'ipt'))
      const otherAttrs = computed(() => attrs.value.filter(item => item.attrCls === 'otr'))
      const outputAttrs = computed(() => attrs.value.filter(item => item.attrCls === 'opt'))
      const onUpdateExpandedNames = () => {
        context.emit('on-resize')
      }

      // 添加输入变量
      const addInputAttr = () => {
        dialogCreate(dialog, {
          title: `添加变量`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-variable1', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            if (!data) {
              return false
            }
            data['nodeId'] = nodeData['nodeId']
            data['ndfId'] = nodeData['ndfId']
            data['appId'] = appId
            attrs.value.push(data)
            dialog.loading = true
          }
        }, AddInputAttrForm)
      }
      // 添加输出变量
      const addOutputAttr = () => {
        let attr = {attrId: uuid(), appId, ndfId: nodeData['ndfId'], nodeId: nodeData['nodeId'], attrCls: 'opt', attrKey: '', attrLbl: '', maxLth: 50, notNull: 'N', dataTyp: 'string', attrDesc: '', attrSrc: 'ipt,var', valSrc: 'var', dftVal: '', compTyp: 'input', options: '', builtIn: 'N'}
        attrs.value.push(attr)
      }
      const removeAttr = (attrId) => {
        attrs.value = attrs.value.filter(item => item.attrId !== attrId)
        nodeData['attrs'] = attrs.value
      }
      watch(attrs, () => {
        resizeNode()
      }, {
        deep: true
      })
      return {
        onUpdateExpandedNames,
        defaultExpandedNames: ['input', 'output', ...otherAttrs.value.map(item => item.attrKey)],
        nodeData, attrs, inputAttrs, otherAttrs, outputAttrs,
        addInputAttr, addOutputAttr, removeAttr
      }
    }
  })
</script>
