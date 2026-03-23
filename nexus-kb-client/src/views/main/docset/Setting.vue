<style lang="less">
.kb-docset-setting {
  padding: 24px;
  .n-list {
    .n-list-item {
      margin-top: 10px;
      border: 1px solid var(--n-border-color);
      .n-input--textarea {
        .n-input-wrapper {
          width: 100%;
        }
      }
    }
    .n-list-item:first-child {
      margin-top: 0;
    }
  }
  .value {
    height: 34px;
    line-height: 34px;
  }
  .input {
    display: none;
  }
  .edit {
    .value {
      display: none;
    }
    .input {
      display: block;
    }
  }
}
</style>

<template>
  <div class="kb-docset-setting">
    <n-list hoverable :show-divider="false">
      <n-list-item :class="editSetNm?'edit':''">
        <template #suffix>
          <n-button v-if="editSetNm" @click="onEditSetNm">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editSetNm = !editSetNm">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="名称">
          <div class="value">{{ docsetInfo.setNm }}</div>
          <n-input class="input" v-model:value="setNm" placeholder="请输入文档集名称"/>
        </n-thing>
      </n-list-item>
      <n-list-item :class="editSetDesc?'edit':''">
        <template #suffix>
          <n-button v-if="editSetDesc" @click="onEditSetDesc">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editSetDesc = !editSetDesc">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="介绍">
          <n-ellipsis class="value" :line-clamp="1" :tooltip="{ width: '400px' }">
            {{ docsetInfo.setDesc || '这个文档集还没有介绍~' }}
          </n-ellipsis>
          <n-input class="input" v-model:value="setDesc" type="textarea" placeholder="请输入文档集介绍"
          :autosize="{
            minRows: 3,
            maxRows: 5
          }"/>
        </n-thing>
      </n-list-item>
    </n-list>
  </div>
</template>
<script>
  import { defineComponent, ref, watch, getCurrentInstance } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { isEmpty } from '@/libs/tools'
  import { map2Options } from '@/libs/utils'
  import { COMMON_AUTH_RANGE_TYPE } from '@/libs/enum'
  import ResourceTeam from '@/views/main/components/resource/ResourceTeam.vue'
  import ResourceCoppl from '@/views/main/components/resource/ResourceCoppl.vue'

  export default defineComponent({
    components: {
      ResourceTeam, ResourceCoppl
    },
    props: {
      setId: {
        type: String,
        required: true
      },
      docsetInfo: {
        type: Object
      }
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const setId = props.setId
      const docsetInfo = props.docsetInfo
      const authEdit = computed(() => docsetInfo['optAuth'] === 'alter')
      const setNm = ref(docsetInfo.setNm)
      const setDesc = ref(docsetInfo.setDesc)
      const authRang = ref(docsetInfo.authRang)
      const authRangOptions = ref(map2Options(COMMON_AUTH_RANGE_TYPE))

      const editSetNm = ref(false)
      const onEditSetNm = () => {
        if (isEmpty(setNm.value)) {
          message.error('必须输入文档集名称')
          return
        }
        if (setNm.value === docsetInfo.setNm) {
          editSetNm.value = false
          return
        }
        proxy.$api.put('/doc/docset/name', { setId, setNm: setNm.value }).then(res => {
          docsetInfo.setNm = setNm.value
          editSetNm.value = false
        }).catch(err => {
          console.error(err)
          editSetNm.value = false
        })
      }

      const editSetDesc = ref(false)
      const onEditSetDesc = () => {
        if (isEmpty(setDesc.value)) {
          message.error('必须输入文档集介绍')
          return
        }
        if (setDesc.value === docsetInfo.setDesc) {
          editSetDesc.value = false
          return
        }
        proxy.$api.put('/doc/docset/desc', { setId, setDesc: setDesc.value }).then(res => {
          editSetDesc.value = false
          docsetInfo.setDesc = setDesc.value
        }).catch(err => {
          console.error(err)
          editSetDesc.value = false
        })
      }

      const onAuthRangChange = (rang) => {
        proxy.$api.put('/doc/docset/auth/range', { setId, authRang: rang }).then(res => {
          docsetInfo.authRang = rang
        }).catch(err => {
          console.error(err)
        })
      }

      watch(authRang, (newRang, oldRang) => {
        if (!oldRang) {
          return
        }
        onAuthRangChange(newRang)
      })

      return {
        authEdit,
        docsetInfo,
        setNm, editSetNm, onEditSetNm,
        setDesc, editSetDesc, onEditSetDesc,
        authRang, authRangOptions
      }
    }
  })
</script>
