<style lang="less">
.kb-dataset-link-import {
  .n-icon.icon-delete {
    color: var(--error-color);
    cursor: pointer;
    &:hover {
      color: var(--error-color-hover);
    }
  }
}
</style>
<template>
  <div class="kb-dataset-link-import">
    <n-input v-model:value="linkValue" placeholder="请输入静态网页地址，每行一个，最多10个地址" type="textarea"
      :autosize="{
        minRows: 10,
        maxRows: 20,
      }"
    />
    <n-space vertical style="margin-top: 10px;">
      <p v-for="link in links" :key="link.url">
        <n-input-group>
          <n-input-group-label :style="{ width: '50%' }">{{ link.url }}</n-input-group-label>
          <n-input v-model:value="link.title" placeholder="网页标题">
            <template #suffix>
              <n-icon class="iconfont icon-delete" @click="linkValue = linkValue.replaceAll(link.url, '')" />
            </template>
          </n-input>
        </n-input-group>
      </p>
    </n-space>
  </div>
</template>

<script>
import { defineComponent, getCurrentInstance, computed, ref, watch } from 'vue'
import { } from 'naive-ui'
import { isEmpty, uuid } from '@/libs/tools'
export default defineComponent({
  components: {
  },
  props: {
    reposId: {
      type: String,
      required: true
    },
    catalogId: {
      type: String
    }
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const linkValue = ref('')
    function isValidUrl(url) {
      // 定义URL的正则表达式
      const regex = /^(https?|ftp):\/\/([a-zA-Z0-9.-]+(\:[0-9]+)?)(\/[a-zA-Z0-9%_.~+-]+)*\/?(\?[a-zA-Z0-9%_.,~+-=&]*)?(#[a-zA-Z0-9_-]+)?$/
      return regex.test(url)
    }
    const links = ref([])
    watch(linkValue, (value) => {
      if (isEmpty(value)) {
        links.value = []
        return
      }
      let urls = links.value.map(link => link.url) // 已经有的链接
      let inputs = value.split('\n').filter(link => !isEmpty(link) && isValidUrl(link)) // 输入的有效的链接
      let news = inputs.filter(link => urls.indexOf(link) === -1).map(link => {
        return {
          url: link,
          title: ''
        }
      })
      links.value.push(...news)
      let dels = links.value.filter(link => inputs.indexOf(link.url) === -1)
      links.value = links.value.filter(link => dels.indexOf(link) === -1)
    })
    watch(links, (value) => {
      let links_ = value.filter(item => isEmpty(item.title)).map(link => link.url)
      if (links_.length === 0) {
        return
      }
      proxy.$api.post('/knb/dataset/links/title', links_).then(res => {
        let titles = res.data || {}
        links.value.forEach(link => {
          if (titles[link.url]) {
            link.title = titles[link.url]
          }
        })
      })
    })
    const onSubmit = () => {
      return proxy.$api.post('/knb/dataset/upload/link', {
        reposId: props.reposId, ctlgId: props.catalogId, links: links.value
      })
    }
    const ok = async () => {
      if (links.value.length === 0) {
        return
      }
      await onSubmit()
      return true
    }
    return {
      linkValue, links,
      ok
    }
  }
})
</script>