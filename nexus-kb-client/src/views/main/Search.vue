<style lang="less">
.kb-search.n-card > .n-card__content {
  padding: 0;
  overflow: hidden;
}
.kb-search {
  height: 100%;
  .n-layout {
    height: 100%;
  }
  &-info {
    padding-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    .n-icon {
      font-size: 22px;
      margin-right: 4px;
      color: var(--primary-color);
    }
    .n-icon:last-child {
      color: var(--text-color-3);
      font-size: 14px;
    }
  }
  &-input {
    .n-input__placeholder {
      text-align: center;
    }
  }
  &-option {
    padding-top: 20px;
    padding-bottom: 20px;
    text-align: center;
  }
  &-result, &-history {
    .title {
      padding-bottom: 20px;
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
  }
  &-history {
    height: calc(100% - 385px);
    .list {
      .n-list-item {
        border: 1px solid var(--border-color);
        margin-top: 10px;
        padding: 8px 10px;
        .n-list-item__main {
          align-items: center;
          display: flex;
        }
        .n-list-item__suffix {
          margin-left: 0;
          display: flex;
          .delete.n-button {
            display: none;
            color: var(--error-color);
            &:hover {
              color: var(--error-color-hover);
            }
          }
        }
        &:hover {
          .delete.n-button {
            display: block;
          }
        }
      }
      .n-list-item:first-child {
        margin-top: 0;
      }
    }
  }
  &-result {
    position: relative;
    .list {
      height: calc(100% - 50px);
      .n-list-item {
        background-color: var(--divider-color);
        margin-top: 10px;
      }
      .n-list-item:first-child {
        margin-top: 0;
      }
      .n-thing {
        .n-thing-header {
          .n-tag__content {
            font-size: 12px;
            transform: scale(0.9);
            padding-top: 0.4px;
          }
          .n-tag__icon {
            margin-right: 0;
            .n-icon {
              transform: scale(0.4);
            }
          }
        }
      }
    }
    .n-spin-body {
      position: absolute;
      left: 50%;
      top: 50%;
      margin-left: -17px;
      margin-top: -17px;
    }
  }
}
</style>

<template>
  <n-card class="kb-search" :bordered="false">
    <n-layout has-sider>
      <n-layout-sider bordered :width="350" content-style="padding: 24px;">
        <div class="kb-search-info">
          <n-icon class="iconfont-kb icon-knowledge"></n-icon>
          <n-dropdown trigger="hover" :options="reposOptions" :on-select="onReposSelect">
            <span title="切换对话知识库">{{ selectedRepos.reposNm }}</span>
          </n-dropdown>
          <n-icon class="iconfont icon-unfoldmore"></n-icon>
        </div>
        <div class="kb-search-input">
          <n-input v-model:value="inputValue" type="textarea" autofocus placeholder="请输入搜索文本&#10;搜索 [Enter]/换行 [Ctrl + Enter]" @keydown="onInputKeyDown"
            :autosize="{
              minRows: 10,
              maxRows: 10
            }"
          />
        </div>
        <div class="kb-search-option">
          <n-button type="primary" @click="onSearch" :loading="loading">
            <n-icon class="iconfont-kb icon-search" />&nbsp;搜索
          </n-button>
        </div>
        <div class="kb-search-history">
          <p class="title">
            <n-icon class="iconfont icon-avtimer" />搜索历史
          </p>
          <n-scrollbar class="list">
            <n-list hoverable clickable :show-divider="false">
              <n-list-item v-for="hist in histList" :key="hist.srchId" @click="onSearch(hist.srchText)">
                <n-ellipsis :line-clamp="1">
                  {{ hist.srchText }}
                </n-ellipsis>
                <template #suffix>
                  <n-tag size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                    <n-time :time="Date.now()" :to="new Date(hist.srchTm)" type="relative" />
                  </n-tag>
                  <n-button size="tiny" class="delete" quaternary @click.stop="e => deleteHist(hist, e)" title="删除"><n-icon class="iconfont icon-delete"></n-icon></n-button>
                </template>
              </n-list-item>
            </n-list>
            <n-empty v-if="histList.length === 0"/>
          </n-scrollbar>
        </div>
      </n-layout-sider>
      <n-layout-content class="kb-search-result" content-style="padding: 24px;">
        <p class="title">
          <n-icon class="iconfont-kb icon-search" />搜索结果
        </p>
        <n-scrollbar ref="scrollbarRef" class="list">
          <n-list hoverable clickable :show-divider="false">
            <n-list-item v-for="(result, index) in resultList" :key="result.id + '-' + index" @click="copyToClipboard(result.content)">
              <n-thing title="">
                <template #header>
                  <n-space size="small">
                    <n-tag :bordered="false" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                      相似度:{{ result.score.toFixed(2) }}
                      <template #icon>
                        <n-icon class="iconfont icon-brightness1" />
                      </template>
                    </n-tag>
                  </n-space>
                </template>
                {{ result.content }}
                <template #footer>
                  <n-space size="small">
                    <n-tag :bordered="false" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
                      {{ result.srcNm + '.' + result.srcTyp }}
                      <!-- <template #icon>
                        <n-icon class="iconfont icon-file" />
                      </template> -->
                    </n-tag>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
          <n-empty v-if="resultList.length === 0"/>
        </n-scrollbar>
        <n-spin v-if="loading"></n-spin>
      </n-layout-content>
    </n-layout>
  </n-card>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import _ from 'lodash'
  import { renderIconfontIcon, dialogConfirm } from '@/libs/utils'
  import { localRead, localSave } from '@/libs/tools'
  import { CURRENT_REPOS_ID_KEY } from '@/libs/enum'
  import { isEmpty } from '@/libs/tools'

  export default defineComponent({
    components: {
    },
    setup() {
      const dialog = useDialog()
      const message = useMessage()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const loading = ref(false)
      const inputValue = ref('')
      const selectedReposId = ref('')
      const reposList = ref([])
      const selectedRepos = computed(() => {
        return reposList.value.find(repos => repos.reposId === selectedReposId.value) || {}
      })
      const reposOptions = computed(() => {
        let list = []
        reposList.value.forEach(repos => {
          list.push({
            label: repos.reposNm,
            key: repos.reposId,
            icon: () => renderIconfontIcon('iconfont-kb icon-knowledge')
          },)
        })
        return list
      })
      const initReposList = () => {
        proxy.$api.post('/knb/repository/my/list').then(res => {
          reposList.value = res.data || []
          if (reposList.value.length > 0) {
            let currentId = localRead(CURRENT_REPOS_ID_KEY) || ''
            if (currentId) {
              let fs = reposList.value.filter(repos => repos.reposId === currentId)
              if (fs.length > 0) {
                selectedReposId.value = currentId
                return
              }
            }
            selectedReposId.value = reposList.value[0].reposId
          } else {
            selectedReposId.value = ''
            dialogConfirm(dialog, {
              title: '创建知识库确认',
              content: '您还没有创建知识库，是否去创建一个知识库？',
              type: 'warning',
              onPositiveClick: (e, dialog) => {
                router.push(`/main/repository`)
              }
            })
          }
        }).catch(err => {
          console.error(err)
        })
      }
      initReposList()
      const onReposSelect = (key) => {
        selectedReposId.value = key
        localSave(CURRENT_REPOS_ID_KEY, key)
      }
      const histList = ref([])
      const initHistList = () => {
        proxy.$api.post('/knb/search/hist/my/list', {
          reposId: selectedReposId.value
        }).then(res => {
          histList.value = res.data || []
        }).catch(err => {
          console.error(err)
        })
      }

      const resultList = ref([])
      const onSearch = (text) => {
        if (reposList.value.length === 0) {
          message.error('请先创建知识库')
          dialogConfirm(dialog, {
            title: '创建知识库确认',
            content: '您还没有创建知识库，是否去创建一个知识库？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              router.push(`/main/repository`)
            }
          })
          return
        }
        let noHist = false
        if (typeof text === 'string') {
          inputValue.value = text
          noHist = true
        }
        if (isEmpty(inputValue.value)) {
          return
        }
        loading.value = true
        proxy.$api.post('/knb/search', { reposId: selectedReposId.value, searchTxt: inputValue.value, noHist }).then(res => {
          resultList.value = res.data || []
          initHistList()
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }
      
      const onInputKeyDown = (e) => {
        let keyCode = e.keyCode
        if (keyCode === 13) { // enter
          if (!e.ctrlKey) {
            e.preventDefault()
            onSearch()
          } else {
            inputValue.value += '\n'
          }
        }
      }
      const copyToClipboard = _.debounce(async (text) => {
        try {
          await navigator.clipboard.writeText(text.replace(/<br>/g, '\n'))
          message.success('复制成功')
        } catch (err) {
          console.error('复制失败', err);
        }
      }, 200)
      watch(selectedReposId,(newId, oldId)=>{
        initHistList()
      })
      const deleteHist = (hist) => {
        proxy.$api.delete('/knb/search/hist/' + hist.srchId).then(res => {
          initHistList()
        }).catch(err => {
          console.error(err)
        })
      }
      return {
        loading,
        inputValue,
        selectedRepos,
        reposOptions,
        selectedReposId, resultList, histList,
        onReposSelect, onSearch, onInputKeyDown, copyToClipboard, deleteHist
      }
    }
  })
</script>
