<style lang="less">
.kb-login-form {
  position: relative;
  height: 100%;
  .n-button {
    width: 100%;
  }
  .n-form {
    input:-webkit-autofill,
    input:-internal-autofill-previewed,
    input:-internal-autofill-selected {
      -webkit-box-shadow: 0 0 0px 1000px transparent inset !important;
      -webkit-text-fill-color: var(--n-text-color);
      background-color: transparent !important;
      transition: background-color 50000s ease-in-out 0s;
    }
    input:first-line{
      font-size: var(--n-font-size);
      color: var(--n-text-color);
    }
    .n-form-item.captcha {
      .n-form-item-blank {
        position: relative;
        p {
          position: absolute;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 1px solid var(--border-color);
          border-radius: var(--border-radius);
          cursor: pointer;
          color: var(--text-color-3);
          &:hover {
            background-color: var(--primary-color-opacity-5);
          }
        }
      }
    }
  }
  .kb-login-vcode {
    position: absolute;
    left: 50%;
    top: 50%;
    margin-top: -170px;
    margin-left: -199px;
    display: none;
    .range-box {
      background-color: var(--n-color);
      box-shadow: 0 0 8px var(--primary-color-opacity-3) inset;
      .range-slider {
        background-color: var(--primary-color-opacity-5);
      }
      .range-btn {
        background-color: var(--primary-color) !important;
        box-shadow: none !important; // 0 0 4px var(--primary-color-opacity-5);
      }
    }
  }
  .kb-login-vcode.vcode-show {
    display: block;
  }
}
</style>

<template>
  <div class="kb-login-form">
    <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" :show-label="false" @keydown.enter.native="onSubmit">
      <n-form-item path="username">
        <n-input v-model:value="formData.username" placeholder="登录账号" size="large" @keydown.enter.prevent>
          <template #prefix>
            <n-icon class="iconfont icon-account" />
          </template>
        </n-input>
      </n-form-item>
      <n-form-item path="password">
        <n-input v-model:value="formData.password" placeholder="登录密码" type="password" size="large" @keydown.enter.prevent>
          <template #prefix>
            <n-icon class="iconfont icon-lock" />
          </template>
        </n-input>
      </n-form-item>
      <n-form-item path="captcha" class="captcha">
        <n-radio-group size="large">
          <n-radio-button v-model:value="formData.captcha" value="success" style="visibility: hidden;"/>
        </n-radio-group>
        <p @click="vcodeShow = !vcodeShow">
          <span v-if="Boolean(formData.captcha)" style="color: var(--success-color)">验证成功</span>
          <span v-else>请点击完成拼图验证</span>
        </p>
      </n-form-item>
    </n-form>
    <n-button type="primary" :loading="logining" :disabled="!Boolean(formData.username) || !Boolean(formData.password)" @click="onSubmit">
      <n-icon class="iconfont icon-login" />&nbsp;登录
    </n-button>
    <div :class="[`kb-login-vcode`, `${vcodeShow ? 'vcode-show' : ''}`]" v-on-click-outside="onVcodeClick">
      <Vcode ref="vcodeRef" :show="true" type="inside" :canvasWidth="399" @success="onVcodeSuccess" @reset="onVcodeReset" @fail="onVcodeReset" sliderText="请拖动完成拼图验证" />
    </div>
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import Vcode from 'vue3-puzzle-vcode'
  import { aes_encrypt } from '@/libs/secret'
  import useUserStore from '@/store/user'
  import { vOnClickOutside } from '@vueuse/components'

  export default defineComponent({
    components: {
      Vcode
    },
    directives: {
      onClickOutside: vOnClickOutside
    },
    setup() {
      const { proxy, ctx } = getCurrentInstance()
      const message = useMessage()
      const router = useRouter()
      const userStore = useUserStore()

      const logining = ref(false)
      const formRef = ref(null)
      const vcodeRef = ref(null)
      const formData = ref({
        username: '',
        password: '',
        captcha: ''
      })
      const formRules = ref({
        username: [
          { required: true, message: '请输入登录账号', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入登录密码', trigger: 'blur' }
        ],
        captcha: [
          { required: true, message: '请滑动滑块验证', trigger: 'change' }
        ]
      })
      const vcodeShow = ref(false)
      const onVcodeClick = (e) => {
        // if (e.target.nodeName === 'CANVAS' || e.target.nodeName === 'IMG') {
        //   return
        // }
        vcodeShow.value = false
      }
      const onVcodeReset = () => {
        formData.value.captcha = ''
      }
      const onVcodeSuccess = () => {
        formData.value.captcha = 'success'
        vcodeShow.value = false
      }
      const doLogin = () => {
        logining.value = true
        proxy.$api.post('/sys/auth/login', { username: formData.value.username, password: aes_encrypt(formData.value.password) }).then(res => {
          if (res.success) {
            message.success('登录成功')
            const { id, name, token } = res.data
            userStore.setToken(token)
            userStore.setInfo({
              id, name
            })
            router.push({
              path: '/'
            })
          }
          logining.value = false
        }).catch(err => {
          message.error(err.msg)
          logining.value = false
          vcodeRef.value?.reset(true)
        })
      }
      const onSubmit = (e) => {
        e.preventDefault()
        formRef.value?.validate((errors) => {
          if (!errors) {
            doLogin()
          } else {
            console.log(errors)
          }
        })
      }
      return {
        logining,
        formRef, vcodeRef,
        formData, formRules,
        vcodeShow,
        onVcodeClick, onSubmit, onVcodeReset, onVcodeSuccess
      }
    }
  })
</script>
