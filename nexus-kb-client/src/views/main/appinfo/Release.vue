<style lang="less">
.kb-flow-release {
  .n-timeline {
    .n-timeline-item-timeline__circle {
      border-color: var(--primary-color) !important;
    }
  }
}
</style>

<template>
  <div class="kb-flow-release">
    <n-timeline>
      <n-timeline-item v-for="release in releaseList" :key="release.rlseId" type="info">
        <n-time :time="new Date(release.rlseTm)" format="yyyy-MM-dd hh:mm" />
      </n-timeline-item>
    </n-timeline>
    <n-empty v-if="releaseList.length === 0"/>
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed } from 'vue'

  export default defineComponent({
    components: {
    },
    props: {
      appId: String
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const appId = props.appId
      const releaseList = ref([])
      const initReleaseList = () => {
        proxy.$api.get(`/agt/app/release/list/${appId}`).then(res => {
          releaseList.value = res.data
        })
      }
      initReleaseList()
      return {
        releaseList
      }
    }
  })
</script>
