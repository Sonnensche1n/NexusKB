<style lang="less">
@import url('@/views/main/detail.less');
</style>

<template>
  <n-card class="kb-menu-detail" :bordered="false">
    <n-layout has-sider>
      <n-layout-sider bordered content-style="padding: 24px;" :default-collapsed="true" collapse-mode="width" show-trigger :collapsed-width="58">
        <div class="kb-menu-detail-title" :title="reposInfo.reposNm">
          <n-icon class="iconfont-kb icon-knowledge"></n-icon>
          <span>{{ reposInfo.reposNm }}</span>
        </div>
        <n-menu class="kb-menu-detail-menu"
          v-model:value="activeKey"
          :options="menuOptions"
          responsive
          :on-update:value="onMenuUpdate"
        />
      </n-layout-sider>
      <n-layout-content content-style="padding: 24px;" v-if="inited">
        <dataset v-if="activeKey === 'dataset'" :reposId="route.query.id" :reposInfo="reposInfo" :authEdit="authEdit"/>
        <setting v-if="activeKey === 'setting'" :reposId="route.query.id" :reposInfo="reposInfo" :authEdit="authEdit" />
        <qanswer v-if="activeKey === 'qanswer'" :reposId="route.query.id" :reposInfo="reposInfo" :authEdit="authEdit" />
      </n-layout-content>
    </n-layout>
  </n-card>
</template>
<script>
  import { defineComponent, ref, watch, getCurrentInstance } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { NLayout, NLayoutSider, NLayoutContent, NMenu, NCard } from 'naive-ui'
  import { renderIconfontIcon } from '@/libs/utils'
  import Dataset from './Dataset.vue'
  import Setting from './Setting.vue'
  import Qanswer from './Qanswer.vue'

  const menuOptions = [
    {
      label: '数据集',
      key: 'dataset',
      icon: () => renderIconfontIcon('iconfont-kb icon-dataset1')
    },
    {
      label: 'Q&A',
      key: 'qanswer',
      icon: () => renderIconfontIcon('iconfont-kb icon-qa')
    },
    {
      label: '设置',
      key: 'setting',
      icon: () => renderIconfontIcon('iconfont icon-settings')
    }
  ]
  export default defineComponent({
    components: {
      NLayout, NLayoutSider, NLayoutContent, NMenu, NCard,
      Dataset, Setting, Qanswer
    },
    setup() {
      const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const route = useRoute()
      const activeKey = ref(router.currentRoute.value.query.menu || 'dataset')
      const onMenuUpdate = (key) => {
        router.push(`/main/repository/detail?menu=${key}&id=${route.query.id}`)
      }
      watch(() => route.query, (newRouter) => {
        activeKey.value = newRouter.menu || 'dataset'
      })
      const reposInfo = ref({})
      const authEdit = computed(() => reposInfo.value['optAuth'] === 'alter')
      const inited = ref(false)
      // 初始化知识库信息
      const initReposInfo = () => {
        proxy.$api.get(`/knb/repository/${route.query.id}`).then(res => {
          reposInfo.value = res.data || {}
          inited.value = true
        }).catch(err => {
          console.error(err)
        })
      }
      initReposInfo()
      return {
        route,
        activeKey,
        menuOptions,
        onMenuUpdate, reposInfo, inited, authEdit
      }
    }
  })
</script>
