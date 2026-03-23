<style lang="less">
.kb-chat-guess {
  padding: 20px;
  .n-card {
    .n-card-header {
      .n-card-header__main {
        font-size: 16px;
      }
    }
  }
  .n-list {
    height: calc(100% - 50px);
    .n-list-item {
      background-color: var(--divider-color);
      margin-top: 10px;
      padding: 6px 12px;
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
}
</style>

<template>
  <div class="kb-chat-guess">
    <n-card hoverable>
      <template #header>
        <n-icon class="iconfont-kb icon-guess" />&nbsp;猜你想问
      </template>
      <n-list hoverable clickable :show-divider="false">
        <n-list-item v-for="quest in questList" :key="quest.srchId" @click="onClick(quest.qstQuest)">
          <n-thing title="">
            {{ quest.qstQuest }}
          </n-thing>
        </n-list-item>
      </n-list>
    </n-card>
  </div>
</template>
<script>
  import { defineComponent, computed } from 'vue'
  export default defineComponent({
    components: {
    },
    props: {
      questList: {
        type: Array,
        default: () => []
      }
    },
    setup(props, context) {
      const onClick = (text) => {
        context.emit('on-quest-change', text)
      }
      return {
        onClick
      }
    }
  })
</script>
