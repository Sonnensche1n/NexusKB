<style lang="less">
@import url('@/views/main/detail.less');
</style>

<template>
  <n-card class="kb-menu-detail" :bordered="false">
    <n-layout has-sider>
      <n-layout-sider bordered content-style="padding: 24px;" style="z-index: 2;" :default-collapsed="true" collapse-mode="width" show-trigger :collapsed-width="58">
        <div class="kb-menu-detail-title" :title="docset.setNm">
          <n-icon class="iconfont-kb icon-docset"></n-icon>
          <span>{{ docset.setNm }}</span>
        </div>
        <n-menu class="kb-menu-detail-menu"
          v-model:value="activeKey"
          :options="menuOptions"
          responsive
          :on-update:value="onMenuUpdate"
        />
      </n-layout-sider>
      <n-layout-content v-if="inited">
        <documents v-if="activeKey === 'document'" :setId="docset.setId" :docsetInfo="docset" />
        <setting v-else-if="activeKey === 'setting'" :setId="docset.setId" :docsetInfo="docset" />
      </n-layout-content>
    </n-layout>
  </n-card>
</template>
<script>
  import { defineComponent, ref, watch, getCurrentInstance } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { renderIconfontIcon } from '@/libs/utils'
  import Documents from './Documents.vue'
  import Setting from './Setting.vue'

  const menuOptions = [
    {
      label: '文档',
      key: 'document',
      icon: () => renderIconfontIcon('iconfont-kb icon-document')
    },
    {
      label: '设置',
      key: 'setting',
      icon: () => renderIconfontIcon('iconfont icon-settings')
    }
  ]
  export default defineComponent({
    components: {
      Documents, Setting
    },
    setup() {
      const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const route = useRoute()
      const activeKey = ref(router.currentRoute.value.query.menu || 'document')
      const onMenuUpdate = (key) => {
        router.push(`/main/docset/detail?menu=${key}&id=${route.query.id}`)
      }
      watch(() => route.query, (newRouter) => {
        activeKey.value = newRouter.menu || 'document'
      })
      const docset = ref({})
      const authEdit = computed(() => docset.value['optAuth'] === 'alter')
      const inited = ref(false)
      // 初始化知识库信息
      const initDocset = () => {
        proxy.$api.get(`/doc/docset/${route.query.id}`).then(res => {
          docset.value = res.data || {}
          inited.value = true
        }).catch(err => {
          console.error(err)
        })
      }
      initDocset()
      return {
        route,
        activeKey,
        menuOptions,
        onMenuUpdate, docset, inited, authEdit
      }
    }
  })
</script>
