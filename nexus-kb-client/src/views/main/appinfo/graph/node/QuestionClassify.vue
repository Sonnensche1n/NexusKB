<style lang="less">
.kb-flow-node-question-classify.n-collapse {
}
</style>

<template>
  <n-collapse class="kb-flow-node-question-classify" :default-expanded-names="defaultExpandedNames" :on-update:expanded-names="onUpdateExpandedNames">
    <n-collapse-item title="用户问题" name="1">
      <template #header-extra>
        <n-select :options="llmSrcOptions" size="small" default-value="slt" style="width: 100px;" @click.stop="" />
      </template>
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item>
          <n-input type="textarea" size="small" :autosize="{ minRows: 2, maxRows: 2 }" />
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <n-collapse-item title="AI模型" name="2">
      <template #header-extra>
        <n-select :options="llmSrcOptions" size="small" default-value="slt" style="width: 100px;" @click.stop="" />
      </template>
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item>
          <n-select :options="llmSrcOptions" size="small" />
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <n-collapse-item title="背景知识" name="3">
      <template #header-extra>
        <n-select :options="llmSrcOptions" size="small" default-value="slt" style="width: 100px;" @click.stop="" />
      </template>
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item>
          <n-input type="textarea" size="small" :autosize="{ minRows: 5, maxRows: 5 }" />
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <n-collapse-item title="分类" name="4">
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item>
          <n-input type="textarea" size="small" :autosize="{ minRows: 1, maxRows: 2 }">
            <template #prefix>
              分类1
            </template>
          </n-input>
        </n-list-item>
        <n-list-item>
          <n-input type="textarea" size="small" :autosize="{ minRows: 1, maxRows: 2 }">
            <template #prefix>
              分类2
            </template>
          </n-input>
        </n-list-item>
        <n-list-item>
          <n-input type="textarea" size="small" :autosize="{ minRows: 1, maxRows: 2 }">
            <template #prefix>
              分类2
            </template>
          </n-input>
        </n-list-item>
        <n-list-item>
          <n-button style="width: 100%;" size="small"><n-icon class="iconfont icon-plus" />&nbsp;添加分类</n-button>
        </n-list-item>
      </n-list>
    </n-collapse-item>
    <n-collapse-item title="输出" name="5">
      <n-list class="kb-var-list" :show-divider="false">
        <n-list-item>
          <span>分类名</span>
          <n-tag size="small">string</n-tag>
        </n-list-item>
      </n-list>
    </n-collapse-item>
  </n-collapse>
</template>
<script>
  import { defineComponent, ref, watch, onMounted } from 'vue'
  
  export default defineComponent({
    components: {
    },
    setup(props, context) {
      const llmSrcOptions = ref([
        {
          label: '变量引用',
          value: 'var'
        },
        {
          label: '手动选择',
          value: 'slt'
        }
      ])
      const onUpdateExpandedNames = () => {
        context.emit('on-resize')
      }
      return {
        onUpdateExpandedNames,
        defaultExpandedNames: ['1', '2', '3', '4'],
        llmSrcOptions
      }
    }
  })
</script>
