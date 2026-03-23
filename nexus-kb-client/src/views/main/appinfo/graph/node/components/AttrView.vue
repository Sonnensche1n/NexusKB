<style lang="less">
</style>

<template>
  <span :title="attr.attrDesc">{{ attr.attrLbl }}</span>
  <n-icon :class="NODE_ATTR_VALUE_DATA_TYPE[attr.dataTyp]?.icon" :title="NODE_ATTR_VALUE_DATA_TYPE[attr.dataTyp]?.label" />
</template>
<script>
import { defineComponent } from 'vue'
import { NODE_ATTR_VALUE_DATA_TYPE } from '@/libs/enum'

export default defineComponent({
  components: {},
  props: {
    attr: Object,
  },
  setup(props, context) {
    return {
      NODE_ATTR_VALUE_DATA_TYPE
    }
  },
});
</script>
