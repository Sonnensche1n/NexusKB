<style lang="less">
.kb-attr-val-input.n-input-group {
  .src-select .n-base-selection {
    height: 100%;
    .n-base-selection-label {
      height: 100%;
      .n-base-selection-input {
        padding: 0;
        text-align: center;
      }
    }
  }
  .n-input-group-label {
    width: 65.39px;
    height: 100%;
    display: flex;
    align-items: center;
    padding: 0 4px;
  }
  .attrkey-input.n-input {
    width: 100px;
    .n-input-wrapper {
      padding: 0 4px;
    }
  }
  .n-input--textarea {
    position: relative;
    .prefix {
      position: absolute;
      right: 4px;
      bottom: 4px;
      line-height: 16px;
      cursor: pointer;
      .n-icon {
        &:hover {
          color: var(--primary-color);
        }
      }
    }
  }
}
</style>

<template>
  <n-input-group class="kb-attr-val-input" @mousedown="onMouseDown">
    <template v-if="attr.attrCls !== 'otr'">
      <n-input-group-label size="small" v-if="attr.builtIn === 'Y'" :title="attr.attrLbl">
        <n-ellipsis>{{ attr.attrLbl }}</n-ellipsis>
      </n-input-group-label>
      <n-input class="attrkey-input" v-else v-model:value="attr.attrKey" placeholder="变量名" size="small" />
    </template>
    <template v-if="attr.valSrc !== 'var'">
      <n-input v-if="attr.compTyp === 'textarea'" v-model:value="attr.attrVal" type="textarea" clearable :placeholder="`请输入${attr.attrLbl}`" size="small">
        <template #prefix>
          <span class="prefix">
            <n-icon class="iconfont-kb icon-enlarge" @click="onEnlarge" />
          </span>
        </template>
      </n-input>
      <n-input-number v-if="attr.compTyp === 'number'" v-model:value="attr.attrVal" :placeholder="`请输入${attr.attrLbl}`" size="small"></n-input-number>
      <n-select v-else-if="attr.compTyp === 'select'" v-model:value="attr.attrVal" :placeholder="`请选择${attr.attrLbl}`" size="small"
        :options="(attr['options'] || '').split(',').map(item => {
          return {
            label: item,
            value: item
          }
        })">
      </n-select>
      <classify v-else-if="attr.compTyp === 'classify'" :attr="attr" />
      <llm v-else-if="attr.compTyp === 'llm'" :attr="attr" />
      <repository v-else-if="attr.compTyp === 'repository'" :attr="attr" />
      <prompt v-else-if="attr.compTyp === 'prompt'" :attr="attr" @on-enlarge="onEnlarge" :key="`prompt-${prompKey}`" />
      <condition v-else-if="attr.compTyp === 'condition'" :attr="attr" />
      <n-input v-else v-model:value="attr.attrVal" type="input" size="small" :placeholder="`请输入${attr.attrLbl}`"></n-input>
    </template>
    <variable v-else :attr="attr" />
    <n-select class="src-select" v-if="(attr.attrSrc || '').split(',').length > 1" v-model:value="attr.valSrc"
      :consistent-menu-width="false" :options="attrSrcOptions"
      :render-label="renderAttrSrcLabel" size="small"
      :default-value="attr.valSrc" style="width: 40px;"
      @click.stop="">
      <template #arrow>
        <span></span>
      </template>
    </n-select>
  </n-input-group>
</template>
<script>
import { defineComponent, watch } from 'vue'
import { useDialog, NIcon } from 'naive-ui'
import { dialogCreate, renderIconfontIcon } from '@/libs/utils'
import { isEmpty } from '@/libs/tools'
import _ from 'lodash'
import { NODE_ATTR_VALUE_SOURCE_TYPE } from '@/libs/enum'
import { useNode } from '../../mixin/node'
import Classify from './input/Classify.vue'
import Llm from './input/Llm.vue'
import Repository from './input/Repository.vue'
import Variable from './input/Variable.vue'
import Condition from './input/Condition.vue'
import Prompt from './input/Prompt.vue'
import InputEnlargeForm from './form/InputEnlargeForm.vue'

// attr.compTyp 前端组件: input,textarea,number,select,repostory知识库选择器,llm模型选择器,variable变量选择器 等等
export default defineComponent({
  components: {
    Variable, Classify, Llm, Repository, Condition, Prompt
  },
  props: {
    attr: Object,
  },
  setup(props, context) {
    const dialog = useDialog()
    const { resizeNode } = useNode()
    let attr = props.attr
    const getAttrSrcOptions = (attr) => {
      let attrSrc = attr.attrSrc || ''
      let options = []
      for (let key in NODE_ATTR_VALUE_SOURCE_TYPE) {
        if (attrSrc.indexOf(key) > -1) {
          options.push(NODE_ATTR_VALUE_SOURCE_TYPE[key])
        }
      }
      return options
    }
    watch(() => attr.valSrc, () => {
      attr.attrVal = ''
      resizeNode()
    })
    watch(() => attr.attrVal, (newVal) => {
      if (attr.valSrc !== 'var') {
        return
      }
      if (attr.builtIn !== 'Y') {
        if (isEmpty(newVal)) {
          attr.attrKey = ''
          return
        }
        let vals = newVal.split('/')
        attr.attrKey = vals[vals.length - 1]
      }
    })

    const onMouseDown = _.debounce(() => {
      resizeNode()
    }, 500)

    const prompKey = ref(0)
    const onEnlarge = () => {
      dialogCreate(dialog, {
        title: attr.attrLbl,
        style: 'width: 60%;',
        maskClosable: false,
        negativeText: '',
        positiveText: '',
        icon: () => renderIconfontIcon('iconfont-kb icon-text', { size: '28px' }),
        onClose: () => {
          if (attr.compTyp === 'prompt') {
            prompKey.value++
          }
        }
      }, InputEnlargeForm, {
        attr
      })
    }

    return {
      tagColor: {color: 'var(--primary-color-opacity-5)', borderColor: 'var(--primary-color-opacity-3)', textColor: 'var(--primary-color)'},
      attrSrcOptions: getAttrSrcOptions(attr),
      renderAttrSrcLabel: (option) => {
        return [
          h(
            NIcon,
            {
              title: option.label,
              class: option.icon
            }
          )
        ]
      },
      onMouseDown, onEnlarge, prompKey
    }
  },
});
</script>
