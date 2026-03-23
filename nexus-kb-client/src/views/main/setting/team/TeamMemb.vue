<style lang="less">
.kb-team-memb {
  padding: 0 24px;
  &-header {
    padding-bottom: 10px;
    display: flex;
    justify-content: space-between;
    .title {
      font-size: 18px;
      font-weight: 600;
      .n-icon {
        font-size: 22px;
        margin-right: 4px;
        position: relative;
        top: 2px;
        color: var(--primary-color);
      }
    }
    .option {
      display: flex;
      .n-input {
        margin-right: 10px;
      }
    }
  }
}
</style>

<template>
  <div class="kb-team-memb">
    <div class="kb-team-memb-header">
      <div class="title">
        <n-icon class="iconfont-kb icon-user"></n-icon>成员({{ membList.length }})
      </div>
      <div class="option">
        <n-button v-if="authEdit" type="primary" @click="onInvite"><n-icon class="iconfont icon-plus"></n-icon>&nbsp;邀请成员</n-button>
      </div>
    </div>
    <n-data-table :loading="loading" :columns="columns" :data="membList" />
  </div>
</template>
<script>
  import { defineComponent, ref, computed, getCurrentInstance, h } from 'vue'
  import { NTag, NBadge, NButton, NIcon, NDropdown, useDialog } from 'naive-ui'
  import InviteMemb from './InviteMemb.vue'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { AUTH_TEAM_ROLE_TYPE } from '@/libs/enum'
  export default defineComponent({
    components: {
    },
    props: {
      teamId: {
        type: String,
        required: true
      },
      team: {
        type: Object
      }
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const teamId = props.teamId
      const team = props.team
      const authEdit = computed(() => team['teamRole'] === 'creator' || team['teamRole'] === 'manager')
      const dialog = useDialog()
      const loading = ref(false)
      const membList = ref([])
      const onInitMembList = () => {
        if (!loading.value) {
          loading.value = true
          proxy.$api.post('/sys/team/member/list', {
            teamId
          }).then(res => {
            membList.value = res.data || []
            loading.value = false
          }).catch(err => {
            console.error(err)
            loading.value = false
          })
        }
      }
      onInitMembList()
      // 邀请成员
      const onInvite = () => {
        dialogCreate(dialog, {
          title: `邀请成员`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-user', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            if (!data || data.length === 0) {
              return
            }
            proxy.$api.post('/sys/team/member/invite', data).then(res => {
              onInitMembList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, InviteMemb, {
          teamId: props.teamId
        })
      }
      const onRemoveMember = (row) => {
        dialogConfirm(dialog, {
          title: '删除',
          content: '确定移除该成员么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.delete('/sys/team/member/' + row.teamId + '/' + row.userId).then(res => {
              onInitMembList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }
      const onMemberRoleAlter = (row) => {
        dialogConfirm(dialog, {
          title: '修改',
          content: '确定修改该成员角色么？',
          type: 'warning',
          onPositiveClick: (e, dialog) => {
            dialog.loading = true
            proxy.$api.post('/sys/team/member/role/alter', row).then(res => {
              onInitMembList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
            return false
          }
        })
      }
      const roleOptions = ref([])
      Object.keys(AUTH_TEAM_ROLE_TYPE).map(key => {
        if (key === 'creator') {
          return
        }
        roleOptions.value.push({
          label: AUTH_TEAM_ROLE_TYPE[key],
          key,
          disabled: false
        })
      })
      return {
        loading,
        authEdit,
        membList,
        columns: [
          { title: '名称', key: 'nkNm', fixed: 'left' },
          { title: '角色', key: 'teamRole', width: 120, render(row) {
            let options = Object.assign([], roleOptions.value)
            options.forEach(item => {
              item.disabled = item.key === row.teamRole
            })
              return h(
                NDropdown,
                {
                  options: authEdit.value ? (row.teamRole === 'creator' ? [] : options) : [],
                  onSelect: (key) => {
                    if (key === row.teamRole) {
                      return
                    }
                    onMemberRoleAlter({ teamId: row.teamId, userId: row.userId, teamRole: key })
                  }
                },
                {
                  default: () => {
                    return [
                      h(
                        NTag,
                        {
                          color: {color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}
                        },
                        {
                          default: () => {
                            return [
                              h(
                                NBadge,
                                {
                                  dot: true,
                                  color: 'var(--primary-color)',
                                  style: {
                                    marginRight: '4px'
                                  }
                                }
                              ),
                              AUTH_TEAM_ROLE_TYPE[row.teamRole] || '成员'
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
                title: '移除成员',
                disabled: authEdit.value? (row.teamRole === 'creator') : true,
                onClick: () => {
                  onRemoveMember(row)
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
        ],
        onInitMembList, onInvite
      }
    }
  })
</script>
