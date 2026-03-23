<style lang="less">
.kb-input-enlarge-form {
  .kb-flow-node-prompt {
    .option {
      display: none;
    }
  }
}
</style>
<template>
  <n-message-provider>
    <div class="kb-input-enlarge-form">
      <prompt v-if="attr.compTyp === 'prompt'" style="height: 500px;" :attr="attr"/>
      <n-input v-else v-model:value="attr.attrVal" :placeholder="`请输入${attr.attrLbl}`" type="textarea" :rows="20"/>
    </div>
  </n-message-provider>
</template>

<script>
import { defineComponent } from 'vue'
import Prompt from '../input/Prompt.vue'
export default defineComponent({
  components: {
    Prompt
  },
  props: {
    attr: Object
  },
  setup(props) {
    return {
    }
  }
})
</script>