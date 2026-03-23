<style lang="less">
.kb-llm {
  .n-scrollbar-content>.n-collapse>.n-collapse-item {
    border-top: 0;
    .n-form .n-form-item-feedback-wrapper {
      display: none;
    }
    .n-collapse-item__header {
      padding: 0;
    }
    .n-grid {
      .n-card {
        position: relative;
        cursor: pointer; 
        .n-card-cover {
          padding: 10px 10px 0 10px;
          img {
            height: 1.5rem;
            width: auto;
            max-width: 100%;
          }
        }
        .n-card__footer {
          .n-space {
            gap: 4px !important;
          }
        }
        .n-card__action {
          align-items: center;
          justify-content: center;
          width: 100%;
          padding: 0;
          gap: 10px;
          display: none;
          position: absolute;
          bottom: 10px;
        }
        &:hover {
          border-color: var(--primary-color);
          .n-card__footer {
            visibility: hidden;
          }
          .n-card__action {
            background-color: initial;
            display: flex;
          }
        }
      }
    }
  }
}
</style>

<template>
  <n-scrollbar class="kb-llm">
    <n-collapse :default-expanded-names="['pfrce ', 'list', 'prvd']" display-directive="show">
      <n-collapse-item title="模型首选项" name="pfrce ">
        <model-preference ref="mpRef" />
      </n-collapse-item>
      <n-collapse-item title="已设置模型" name="list">
        <n-empty v-if="myLlmPrvdList.length === 0"/>
        <n-grid y-gap="10" x-gap="10" :cols="1">
          <n-gi v-for="prvd in myLlmPrvdList" :key="prvd.prvdId">
            <n-card embedded hoverable content-style="padding: 10px;" footer-style="padding: 0 10px 10px 10px;">
              <template #cover>
                <img :src="`${origin}${prvd.prvdIcon}`">
              </template>
              <n-ellipsis :line-clamp="4" :tooltip="false" :title="prvd.prvdDesc">
                {{prvd.prvdDesc || '' }}
              </n-ellipsis>
              <prvd-model-list :ref="`model-list-${prvd.prvdId}`" :prvd="prvd"></prvd-model-list>
              <template #footer>
                <n-space :wrap="false">
                  <n-tag v-for="typ in prvd.modlTyp?.split(',')" :key="`${prvd.prvdId}-${typ}`" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                    {{ typ }}
                  </n-tag>
                </n-space>
              </template>
              <template #action>
                <n-button size="small" @click="onPrvdSetting(prvd, true)">
                  <n-icon class="iconfont icon-settings"></n-icon>&nbsp;设置
                </n-button>
                <n-button size="small" @click="onAddModel(prvd, true)">
                  <n-icon class="iconfont icon-plus"></n-icon>&nbsp;添加模型
                </n-button>
                <n-button size="small" type="error" @click="onRemovePrvd(prvd)" v-if="prvd.prvdId !== 'default'">
                  <n-icon class="iconfont icon-delete"></n-icon>&nbsp;移除
                </n-button>
              </template>
            </n-card>
          </n-gi>
        </n-grid>
      </n-collapse-item>
      <n-collapse-item title="未设置模型" name="prvd">
        <n-empty v-if="llmPrvdList.length === 0"/>
        <n-grid x-gap="10" y-gap="10" :cols="4">
          <n-gi v-for="prvd in llmPrvdList" :key="prvd.prvdId">
            <n-card embedded hoverable content-style="padding: 10px;" footer-style="padding: 0 10px 10px 10px;">
              <template #cover>
                <img :src="`${origin}${prvd.prvdIcon}`">
              </template>
              <n-ellipsis style="height: 86px;" :line-clamp="4" :tooltip="false" :title="prvd.prvdDesc">
                {{prvd.prvdDesc || '' }}
              </n-ellipsis>
              <template #footer>
                <n-space :wrap="false">
                  <n-tag v-for="typ in prvd.modlTyp?.split(',')" :key="`${prvd.prvdId}-${typ}`" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                    {{ typ }}
                  </n-tag>
                </n-space>
              </template>
              <template #action>
                <n-button size="small" @click="onPrvdSetting(prvd, false)">
                  <n-icon class="iconfont icon-settings"></n-icon>&nbsp;设置
                </n-button>
                <n-button size="small" @click="onAddModel(prvd, false)">
                  <n-icon class="iconfont icon-plus"></n-icon>&nbsp;添加模型
                </n-button>
              </template>
            </n-card>
          </n-gi>
        </n-grid>
      </n-collapse-item>
    </n-collapse>
  </n-scrollbar>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, watch, computed } from 'vue'
  import { useMessage, useDialog } from 'naive-ui'
  import { dialogCreate, dialogConfirm, renderIconfontIcon } from '@/libs/utils'
  import { baseOrigin } from '@/config'
  import PrvdSettingForm from './llm/PrvdSettingForm.vue'
  import PrvdModelForm from './llm/PrvdModelForm.vue'
  import PrvdModelList from './llm/PrvdModelList.vue'
  import ModelPreference from './llm/ModelPreference.vue'

  export default defineComponent({
    components: {
      PrvdModelList, ModelPreference
    },
    setup() {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const origin = baseOrigin
      
      const mpRef = ref()
      const allLlmPrvdList = ref([])
      const myLlmPrvdList = ref([])
      const initMyLlmPrvdList = () => {
        proxy.$api.post('/sys/model/prvd/my/list').then(res => {
          myLlmPrvdList.value = res.data || []
        }).catch(err => {
          console.error(err)
        })
      }
      initMyLlmPrvdList()
      const initAllLlmPrvdList = () => {
        proxy.$api.post('/sys/model/prvd/list').then(res => {
          allLlmPrvdList.value = res.data || []
        }).catch(err => {
          console.error(err)
        })
      }
      initAllLlmPrvdList()

      const llmPrvdList = computed(() => {
        return allLlmPrvdList.value.filter(prvd => {
          return !myLlmPrvdList.value.find(myPrvd => myPrvd.prvdId === prvd.prvdId)
        })
      })

      const onRemovePrvd = (prvd) => {
        dialogConfirm(dialog, {
          title: '确认',
          content: '确定移除该供应商配置么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/sys/model/setting/' + prvd.prvdId).then(res => {
              myLlmPrvdList.value = myLlmPrvdList.value.filter(myPrvd => myPrvd.prvdId !== prvd.prvdId)
              mpRef.value.resetSelector()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }

      const onPrvdSetting = (prvd, setted = false) => {
        dialogCreate(dialog, {
          title: `设置 ${prvd.prvdNm}`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont icon-settings', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/sys/model/param/prvd/' + prvd.prvdId, data).then(res => {
              if (!setted) {
                myLlmPrvdList.value.push(prvd)
                mpRef.value.resetSelector()
              }
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, PrvdSettingForm, {
          prvd
        })
      }
      
      const onAddModel = (prvd, setted = false) => {
        dialogCreate(dialog, {
          title: `设置 ${prvd.prvdNm}`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont icon-settings', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/sys/model/prvd/modl/' + prvd.prvdId, data).then(res => {
              if (!setted) {
                myLlmPrvdList.value.push(prvd)
              }
              let refs = ctx.$refs[`model-list-${prvd.prvdId}`]
              if (refs) {
                refs[0]?.initModelList()
              }
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, PrvdModelForm, {
          prvd
        })
      }

      return {
        origin,
        mpRef,
        myLlmPrvdList, llmPrvdList,
        onPrvdSetting, onAddModel, onRemovePrvd
      }
    }
  })
</script>
