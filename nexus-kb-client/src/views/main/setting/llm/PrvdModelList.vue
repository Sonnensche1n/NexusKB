<style lang="less">
.kb-llm-model-list.n-collapse {
  .n-collapse-item {
    margin-left: 0;
    .n-collapse-item__header-main {
      font-size: var(--font-size-mini);
    }
    .n-collapse-item__content-inner {
      padding-top: 0;
    }
  }
  .n-list {
    .n-list-item {
      cursor: pointer;
      padding: 4px;
      border-radius: var(--border-radius);
      &:hover {
        background-color: var(--primary-color-opacity-5);
      }
      .n-list-item__divider {
        display: none;
      }
      .n-thing {
        .n-thing-avatar {
          margin-top: 0;
          margin-right: 2px;
          display: flex;
          align-items: center;
          .n-avatar {
            background-color: initial;
            width: 16px;
            height: 16px;
          }
          .n-avatar__text {
            position: relative;
          }
        }
        .n-thing-avatar-header-wrapper {
          align-items: center;
          .n-thing-header {
            .n-thing-header__title {
              font-size: var(--font-size-mini);
            }
            .n-thing-header__extra {
              .n-tag.option {
                position: relative;
                top: 1px;
                cursor: pointer;
                &:hover {
                  background-color: var(--primary-color);
                  .n-icon {
                    color: #fff;
                  }
                }
              }
            }
          }
        }
        .n-thing-main .n-thing-header {
          margin-bottom: 0;
        }
      }
    }
  }
}
</style>
<template>
  <n-collapse class="kb-llm-model-list" :on-update:expanded-names="(expandedNames) => {
    titlePrefix = expandedNames.length === 0 ? '展开' : '收起'
  }">
    <n-collapse-item :title="`${titlePrefix}${modelList.length}个模型`" name="list">
      <n-list>
        <n-empty v-if="modelList.length === 0"/>
        <n-list-item v-for="model in modelList" :key="`${model.prvdId}-${model.modlNm}`">
          <n-thing>
            <template #avatar>
              <n-avatar>
                <img :src="`${origin}${model.modlIcon || '/static/images/model/default_small.png'}`">
              </n-avatar>
            </template>
            <template #header>
              {{ model.modlNm }}
            </template>
            <template #header-extra>
              <n-space style="gap: 4px;">
                <n-tag size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                  {{ model.modlTyp }}
                </n-tag>
                <template v-if="model.builtIn === 'N'">
                  <n-tag size="small" title="设置" class="option" @click="onEditModel(model)"  :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                    <n-icon class="iconfont icon-settings" />
                  </n-tag>
                  <n-tag size="small" title="移除" class="option" type="error" @click="onRemoveModel(model)">
                    <n-icon class="iconfont icon-delete" />
                  </n-tag>
                </template>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-collapse-item>
  </n-collapse>
</template>

<script>
import { defineComponent, getCurrentInstance, ref, computed } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { isEmpty } from '@/libs/tools'
import { baseOrigin } from '@/config'
import { dialogCreate, dialogConfirm, renderIconfontIcon } from '@/libs/utils'
import PrvdModelForm from './PrvdModelForm.vue'

export default defineComponent({
  components: {
  },
  props: {
    prvd: Object
  },
  setup(props) {
    const dialog = useDialog()
    const message = useMessage()
    const { proxy, ctx } = getCurrentInstance()
    const { prvdId, prvdNm } = props.prvd
    const origin = baseOrigin
    const titlePrefix = ref('展开')
    const modelList = ref([])
    const initModelList = () => {
      proxy.$api.get('/sys/model/prvd/modl/my/list/' + prvdId).then(res => {
        modelList.value = res['data']
      })
    }
    initModelList()

    const onEditModel = (model) => {
      dialogCreate(dialog, {
        title: `设置 ${prvdNm}`,
        style: 'width: 40%;',
        maskClosable: false,
        icon: () => renderIconfontIcon('iconfont icon-settings', { size: '28px' }),
        onPositiveClick: (data, e, dialog) => {
          proxy.$api.post('/sys/model/prvd/modl/' + prvdId, data).then(res => {
            dialog.destroy()
          }).catch(err => {
            console.error(err)
            dialog.destroy()
          })
        }
      }, PrvdModelForm, {
        prvd: props.prvd, model
      })
    }

    const onRemoveModel = (model) => {
      dialogConfirm(dialog, {
        title: '确认',
        content: '确定移除该模型么？',
        type: 'warning',
        onPositiveClick: (e, dialog) => {
          dialog.loading = true
          proxy.$api.delete('/sys/model/prvd/modl/' + model.modlId).then(res => {
            initModelList()
            dialog.destroy()
          }).catch(err => {
            console.error(err)
            dialog.destroy()
          })
          return false
        }
      })
      
    }
    return {
      origin, titlePrefix,
      modelList, initModelList, onEditModel, onRemoveModel
    }
  }
})
</script>