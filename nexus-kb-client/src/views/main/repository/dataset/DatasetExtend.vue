<style lang="less">
.kb-dataset-extend {
  height: 100%;
  .header {
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 10px;
    .n-menu.n-menu--horizontal {
      width: auto;
    }
    .n-icon {
      font-size: 22px;
      margin-right: 4px;
      color: var(--primary-color);
      cursor: pointer;
      &:hover {
        color: var(--primary-color-opacity-2);
      }
    }
    .title {
      .n-icon {
        position: relative;
        top: 1px;
      }
    }
  }
  &>.content {
    height: calc(100% - 52px);
  }
}
</style>

<template>
  <div class="kb-dataset-extend">
    <div class="header">
      <div class="title"><n-icon class="iconfont icon-undovariant" title="返回" @click="onTurnBack"></n-icon>{{ dtsetNm }}</div>
      <n-menu v-model:value="activeKey" mode="horizontal" :options="menuOptions" responsive/>
    </div>
    <div class="content">
      <chunk v-if="activeKey === 'chunk'" :reposId="reposId" :dtsetId="dtsetId" :authEdit="authEdit" />
      <qanswer v-else-if="activeKey === 'qanswer'" :reposId="reposId" :dtsetId="dtsetId" :authEdit="authEdit" />
      <precis v-if="activeKey === 'precis'" :reposId="reposId" :dtsetId="dtsetId" :authEdit="authEdit" />
      <triplet v-else-if="activeKey === 'triplet'" :reposId="reposId" :dtsetId="dtsetId" :authEdit="authEdit" />
    </div>
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import Chunk from './Chunk.vue'
  import Qanswer from '../Qanswer.vue'
  import Precis from './Precis.vue'
  import Triplet from './Triplet.vue'

  export default defineComponent({
    components: {
      Chunk, Qanswer, Precis, Triplet
    },
    props: {
      reposId: String,
      dtsetId: String,
      dtsetNm: String,
      authEdit: Boolean
    },
    setup(props, context) {
      const onTurnBack = () => {
        context.emit('on-turn-back')
      }
      const activeKey = ref('chunk')
      const menuOptions = [
        {
          label: '分段',
          key: 'chunk',
          icon: () => renderIconfontIcon('iconfont-kb icon-dataset1')
        },
        {
          label: '摘要',
          key: 'precis',
          icon: () => renderIconfontIcon('iconfont-kb icon-document')
        },
        {
          label: 'Q&A',
          key: 'qanswer',
          icon: () => renderIconfontIcon('iconfont-kb icon-qa')
        },
        {
          label: '图谱',
          key: 'triplet',
          icon: () => renderIconfontIcon('iconfont-kb icon-triplet1')
        }
      ]
      return {
        activeKey, menuOptions,
        onTurnBack
      }
    }
  })
</script>
