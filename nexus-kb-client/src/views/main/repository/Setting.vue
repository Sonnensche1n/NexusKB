<style lang="less">
.kb-repos-setting {
  .n-list {
    .n-list-item {
      margin-top: 10px;
      border: 1px solid var(--border-color);
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
  <div class="kb-repos-setting">
    <n-list hoverable :show-divider="false">
      <n-list-item :class="editReposNm?'edit':''">
        <template #suffix>
          <n-button v-if="editReposNm" @click="onEditReposNm">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editReposNm = !editReposNm">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="名称">
          <div class="value">{{ reposInfo.reposNm }}</div>
          <n-input class="input" v-model:value="reposNm" placeholder="请输入知识库名称"/>
        </n-thing>
      </n-list-item>
      <n-list-item :class="editReposDesc?'edit':''">
        <template #suffix>
          <n-button v-if="editReposDesc" @click="onEditReposDesc">
            <n-icon class="iconfont icon-check" />&nbsp;提交
          </n-button>
          <template v-else>
            <n-button v-if="authEdit" @click="editReposDesc = !editReposDesc">
              <n-icon class="iconfont icon-pencil" />&nbsp;修改
            </n-button>
          </template>
        </template>
        <n-thing title="介绍">
          <n-ellipsis class="value" :line-clamp="1" :tooltip="{ width: '400px' }">
            {{ reposInfo.reposDesc || '这个知识库还没有介绍~' }}
          </n-ellipsis>
          <n-input class="input" v-model:value="reposDesc" type="textarea" placeholder="请输入知识库介绍"
          :autosize="{
            minRows: 3,
            maxRows: 5
          }"/>
        </n-thing>
      </n-list-item>
      <n-list-item class="kb-repos-auth">
        <n-thing title="配置">
          <repository-setting :reposId="reposId" :authEdit="authEdit" />
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
  import RepositorySetting from './setting/RepositorySetting.vue'

  export default defineComponent({
    components: {
      ResourceTeam, ResourceCoppl, RepositorySetting
    },
    props: {
      reposId: {
        type: String,
        required: true
      },
      reposInfo: {
        type: Object
      },
      authEdit: {
        type: Boolean
      }
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const reposId = props.reposId
      const reposInfo = props.reposInfo
      const authEdit = props.authEdit
      const reposNm = ref(reposInfo.reposNm)
      const reposDesc = ref(reposInfo.reposDesc)
      const authRang = ref(reposInfo.authRang)
      const authRangOptions = ref(map2Options(COMMON_AUTH_RANGE_TYPE))

      const editReposNm = ref(false)
      const onEditReposNm = () => {
        if (isEmpty(reposNm.value)) {
          message.error('必须输入知识库名称')
          return
        }
        if (reposNm.value === reposInfo.reposNm) {
          editReposNm.value = false
          return
        }
        proxy.$api.put('/knb/repository/name', { reposId, reposNm: reposNm.value }).then(res => {
          reposInfo.reposNm = reposNm.value
          editReposNm.value = false
        }).catch(err => {
          console.error(err)
          editReposNm.value = false
        })
      }

      const editReposDesc = ref(false)
      const onEditReposDesc = () => {
        if (isEmpty(reposDesc.value)) {
          message.error('必须输入知识库介绍')
          return
        }
        if (reposDesc.value === reposInfo.reposDesc) {
          editReposDesc.value = false
          return
        }
        proxy.$api.put('/knb/repository/desc', { reposId, reposDesc: reposDesc.value }).then(res => {
          editReposDesc.value = false
          reposInfo.reposDesc = reposDesc.value
        }).catch(err => {
          console.error(err)
          editReposDesc.value = false
        })
      }
      const onAuthRangChange = (rang) => {
        proxy.$api.put('/knb/repository/auth/range', { reposId, authRang: rang }).then(res => {
          reposInfo.authRang = rang
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
        reposInfo,
        reposNm, editReposNm, onEditReposNm,
        reposDesc, editReposDesc, onEditReposDesc,
        authRang, authRangOptions
      }
    }
  })
</script>
