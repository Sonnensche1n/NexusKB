<style lang="less">
.kb-card-list {
  .n-card {
    position: relative;
    cursor: pointer;
    border-radius: 10px;
    &::before {
      content: '';
      position: absolute;
      height: 15px;
      width: 12px;
      top: 25px;
      left: 0;
      background-color: var(--primary-color);
      border-top-right-radius: 50%;
      border-bottom-right-radius: 50%;
      opacity: var(--opacity-2);
    }
    &::after {
      display: none;
      content: '';
      position: absolute;
      height: 60px;
      width: 10px;
      top: 50%;
      right: 0;
      margin-top: -30px;
      background-color: var(--primary-color);
      border-top-left-radius: 6px;
      border-bottom-left-radius: 6px;
      opacity: var(--opacity-2);
    }
    .n-card__content {
      padding-bottom: 0;
      .iconbg {
        position: absolute;
        font-size: 140px;
        z-index: 0;
        left: 50%;
        top: 1px;
        opacity: 0.05;
        color: var(--primary-color);
      }
      .n-ellipsis {
        height: 45px;
        position: relative;
        z-index: 1;
      }
    }
    .n-card__action {
      padding: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background-color: initial;
    }
  }
}
</style>

<template>
  <n-grid class="kb-card-list" :x-gap="20" :y-gap="20" cols="1 400:2 1000:4">
    <n-gi v-for="item in dataList" :key="item[idKey]">
      <n-card hoverable embedded @click="onItemClick(item[idKey])">
        <template #header>
          <span>{{ item[titleKey] }}</span>
        </template>
        <n-ellipsis :line-clamp="2" :tooltip="{ contentStyle: {width: '260px'} }">
          <template v-if="item[descKey]">
            {{ item[descKey] }}
          </template>
          <template v-else>这个知识库还没有介绍~</template>
        </n-ellipsis>
        <n-icon class="iconbg iconfont-kb icon-scatter"></n-icon>
        <template #action>
          <div></div>
          <n-dropdown v-if="item.optAuth === 'alter'" :options="options" :on-select="(key) => {
            this.onOptionSelect(key, item)
          }">
            <n-icon class="more iconfont icon-dotshorizontal" @click.stop="() => {}"></n-icon>
          </n-dropdown>
        </template>
      </n-card>
    </n-gi>
  </n-grid>
</template>
<script>
  import { defineComponent } from 'vue'
  import { COMMON_AUTH_RANGE_TYPE } from '@/libs/enum'
  import { renderIconfontIcon } from '@/libs/utils'
  export default defineComponent({
    components: {
    },
    props: {
      // 数据
      dataList: {
        type: Array,
        default: () => []
      },
      idKey: 'id',
      titleKey: 'title',
      descKey: 'desc',
      defaultDesc: '还没有介绍~'
    },
    setup(props, context) {
      const options = [
        {
          label: '编辑',
          key: 'edit',
          icon: () => renderIconfontIcon('iconfont icon-pencil')
        },
        {
          label: '删除',
          key: 'delete',
          icon: () => renderIconfontIcon('iconfont icon-delete')
        }
      ]
      const onOptionSelect = (key, item) => {
        context.emit('on-option-select', key, item)
      }
      const onItemClick = (itemId) => {
        context.emit('on-item-click', itemId)
      }
      return {
        options,
        COMMON_AUTH_RANGE_TYPE,
        onOptionSelect, onItemClick
      }
    }
  })
</script>
