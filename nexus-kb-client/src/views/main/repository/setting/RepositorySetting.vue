<style lang="less">
.kb-repos-setting {
  .iconfont.icon-helpcircle {
    margin-left: 4px;
    cursor: pointer;
    &:hover {
      color: var(--primary-color);
    }
  }
}
</style>
<template>
  <n-form
    class="kb-repos-setting"
    ref="formVm"
    label-placement="left"
    label-width="200px"
    :model="formData"
    :rules="formRules"
    require-mark-placement="right-hanging"
    :disabled="!authEdit"
  >
    <n-grid x-gap="10" :cols="2">
      <n-form-item-gi label="最大上下文片段" path="maxCtx">
        <n-input-number v-model:value="formData.maxCtx" placeholder="请输入最大上下文片段" :min="1" :max="20"/>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-icon class="iconfont icon-helpcircle" />
          </template>
          每次聊天或查询将发送到LLM的上下文片段的最大数量。
        </n-tooltip>
      </n-form-item-gi>
      <n-form-item-gi label="聊天历史记录" path="maxHist">
        <n-input-number v-model:value="formData.maxHist" placeholder="请输入聊天历史记录" :min="0" :max="20"/>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-icon class="iconfont icon-helpcircle" />
          </template>
          包含在响应的短期记忆中的先前聊天的数量，推荐 10，过大的值可能导致连续聊天失败，具体取决于消息大小。
        </n-tooltip>
      </n-form-item-gi>
      <n-form-item-gi label="LLM Temperature" path="llmTptur">
        <n-input-number v-model:value="formData.llmTptur" placeholder="请输入LLM Temperature" :min="0"/>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-icon class="iconfont icon-helpcircle" />
          </template>
          通常设置在0和1之间，决定了输出是更随机、更有创意，还是更可预测。温度越高，概率越低，即输出越有创造性。温度越低，概率越高，即输出结果越可预测。
        </n-tooltip>
      </n-form-item-gi>
      <n-form-item-gi label="文档相似性阈值" path="smlrTrval">
        <n-input-number v-model:value="formData.smlrTrval" placeholder="请输入文档相似性阈值" :min="0"/>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-icon class="iconfont icon-helpcircle" />
          </template>
          与聊天相关来源文档分段的最高相似度分数。分数越低，来源与聊天就越相似。
        </n-tooltip>
      </n-form-item-gi>
      <n-form-item-gi label="TopK" path="topK">
        <n-input-number v-model:value="formData.topK" placeholder="请输入TopK" :min="1" :max="20"/>
      </n-form-item-gi>
    </n-grid>
  </n-form>
  <p style="text-align: center;" v-if="authEdit">
    <n-button type="primary" @click="ok" :loading="loading"><n-icon class="iconfont icon-check" />&nbsp;保存</n-button>
  </p>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { isEmpty } from '@/libs/tools'
export default defineComponent({
  components: {
  },
  props: {
    reposId: {
      type: String,
      required: true
    },
    authEdit: false
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const formVm = ref()
    const formData = ref({
      reposId: props.reposId, maxCtx: 20, maxHist: 10, llmTptur: 0.1, smlrTrval: 1, topK: 20
    })
    const initData = () => {
      proxy.$api.get(`/knb/repository/setting/${props.reposId}`).then(res => {
        formData.value = res.data || {}
      }).catch(err => {
        console.error(err)
      })
    }
    initData()
    const formRules = ref({
      maxCtx: [{ required: true, type: 'number', message: '请输入最大上下文片段', trigger: [ 'blur' ]}],
      maxHist: [{ required: true, type: 'number', message: '请输入聊天历史记录', trigger: [ 'blur' ]}],
      llmTptur: [{ required: true, type: 'number', message: '请输入LLM Temperature', trigger: [ 'blur' ]}],
      smlrTrval: [{ required: true, type: 'number', message: '请输入文档相似性阈值', trigger: [ 'blur' ]}],
      topK: [{ required: true, type: 'number', message: '请输入TopK', trigger: [ 'blur' ]}]
    })
    const validate = () => {
      return formVm.value.validate()
    }
    const loading = ref(false)
    const ok = async () => {
      let valid = false
      try {
        await validate()
        valid = true
      } catch (err) {
        // 具体的错误信息项 err
        console.error(err)
      }
      if (valid) {
        loading.value = true
        proxy.$api.post(`/knb/repository/setting`, formData.value).then(res => {
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }
    }
    
    return {
      formVm,
      formData, formRules,
      loading,
      ok
    }
  }
})
</script>