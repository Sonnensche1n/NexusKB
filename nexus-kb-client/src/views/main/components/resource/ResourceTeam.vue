<style lang="less">
</style>

<template>
  <div>
    <div class="option" v-if="authEdit">
      <n-button @click="onTeamRela"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;添加团队</n-button>
    </div>
    <n-data-table style="margin-top: 10px;" :loading="loading" :columns="reposTeamColumns" :data="reposTeamList" />
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { NTag, NBadge, NButton, NIcon, NDropdown, useDialog, useMessage } from 'naive-ui'
  import { map2Options, dialogCreate, dialogConfirm, renderIconfontIcon } from '@/libs/utils'
  import { COMMON_AUTH_OPTION_TYPE } from '@/libs/enum'
  import RelaTeam from './RelaTeam.vue'

  export default defineComponent({
    components: {
    },
    props: {
      rscId: {
        type: String,
        required: true
      },
      rscTyp: {
        type: String,
        required: true
      },
      authEdit: {
        type: Boolean
      }
    },
    setup(props) {
      const dialog = useDialog()
      const message = useMessage()
      const { proxy, ctx } = getCurrentInstance()
      const rscId = props.rscId
      const rscTyp = props.rscTyp
      const authEdit = props.authEdit

      const loading = ref(false)
      const teamAuthOptions = map2Options(COMMON_AUTH_OPTION_TYPE)
      const reposTeamColumns = [
        { title: '名称', key: 'teamNm', fixed: 'left' },
        { title: '权限', key: 'teamAuth', width: 120, render(row) {
          let options = []
          if (authEdit) {
            options = Object.assign([], teamAuthOptions)
            options.forEach(item => {
              item.disabled = item.key === row.teamAuth
            })
          }
            return h(
              NDropdown,
              {
                options,
                onSelect: (key) => {
                  if (key === row.teamAuth) {
                    return
                  }
                  onTeamRoleAlter({ rscId: row.rscId, teamId: row.teamId, teamAuth: key })
                }
              },
              {
                default: () => {
                  return [
                    h(
                      NTag,
                      {
                        type: 'info'
                      },
                      {
                        default: () => {
                          return [
                            h(
                              NBadge,
                              {
                                dot: true, type: 'info',
                                style: {
                                  marginRight: '4px'
                                }
                              }
                            ),
                            COMMON_AUTH_OPTION_TYPE[row.teamAuth] || ''
                          ]
                        }
                      }
                    )
                  ]
                }
              }
            )
          }
        },
        { title: '操作', key: 'option', align: 'center', width: 120, render(row) {
          return h(
            NButton,
            {
              quaternary: true,
              title: '移除团队',
              disabled: !authEdit,
              onClick: () => {
                onRemoveTeam(row)
              }
            },
            {
              default: () => {
                return [
                  h(
                    NIcon,
                    {
                      class: 'iconfont icon-delete'
                    }
                  )
                ]
              }
            })
          }
        }
      ]
      const reposTeamList = ref([])
      const onInitTeamList = () => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.post('/sys/resource/team/list', {
            rscId
          }).then(res => {
            reposTeamList.value = res.data || []
            loading.value = false
          }).catch(err => {
            console.error(err)
            loading.value = false
          })
        }
      }
      onInitTeamList()
      const onTeamRela = () => {
        dialogCreate(dialog, {
          title: `添加团队`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-team', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            if (!data || data.length === 0) {
              return
            }
            proxy.$api.post('/sys/resource/team/rela', data).then(res => {
              onInitTeamList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, RelaTeam, {
          rscId, rscTyp
        })
      }
      const onRemoveTeam = (row) => {
        dialogConfirm(dialog, {
          title: '删除',
          content: '确定移除该团队么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/sys/resource/team/' + row.rscId + '/' + row.teamId).then(res => {
              onInitTeamList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }
      const onTeamRoleAlter = (row) => {
        dialogConfirm(dialog, {
          title: '修改',
          content: '确定修改该团队权限么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.post('/sys/resource/team/auth/alter', row).then(res => {
              onInitTeamList()
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
        authEdit,
        loading, reposTeamColumns, reposTeamList, onTeamRela
      }
    }
  })
</script>
