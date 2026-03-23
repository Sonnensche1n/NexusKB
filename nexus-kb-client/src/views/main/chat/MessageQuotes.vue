<style lang="less">
.kb-mesg-quote.n-list {
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
</style>

<template>
  <n-list class="kb-mesg-quote" hoverable clickable :show-divider="false">
    <n-list-item v-for="(quote, index) in quoteList" :key="quote.mesgId + '-' + index">
      <n-thing title="">
        <template #header>
          <n-space size="small">
            <n-tag :bordered="false" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
              相似度:{{ quote.score.toFixed(2) }}
              <template #icon>
                <n-icon class="iconfont icon-brightness1" />
              </template>
            </n-tag>
          </n-space>
        </template>
        {{ quote.content }}
        <template #footer>
          <n-space size="small">
            <n-tag :bordered="false" size="small" :color="{color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'}">
              {{ quote.dtsetNm + '.' + quote.fileTyp }}
              <template #icon>
                <n-icon class="iconfont icon-file" />
              </template>
            </n-tag>
          </n-space>
        </template>
      </n-thing>
    </n-list-item>
  </n-list>
</template>
<script>
  import { defineComponent, computed } from 'vue'
  export default defineComponent({
    components: {
    },
    props: {
      quoteList: {
        type: Array,
        default: () => []
      }
    },
    setup(props, context) {
      return {
      }
    }
  })
</script>
