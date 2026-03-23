<style lang="less">
.kb-login {
  height: 100%;
  background-image: url(@/assets/images/login-light.jpg);
  background-repeat: no-repeat;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  .n-card {
    width: 500px;
    border-radius: 20px;
    .n-card-header {
      padding: 50px;
      .n-card-header__main {
        line-height: 50px;
        display: flex;
        align-items: center;
        font-weight: 600;
        img {
          height: 50px;
          margin-right: 10px;
        }
        .kb-logo {
          width: 60px;
          height: 60px;
          overflow: hidden;
          margin-right: 10px;
          &-svg {
            transform: scale(0.2);
            margin-left: -100px;
            margin-top: -102px;
          }
        }
      }
    }
    .n-card__content {
      padding: 0 50px 50px 50px;
    }
  }
  &-more {
    padding-top: 20px;
    text-align: right;
    span {
      color: var(--primary-color);
      cursor: pointer;
    }
    span:hover {
      text-decoration: underline;
    }
  }
}
.kb-login.dark {
  background-image: url(@/assets/images/login-dark.jpg);
}
</style>

<template>
  <div :class="`kb-login ${themeType}`">
    <n-card hoverable>
      <template #header>
        <!-- <img src="/logo.png" alt="NexusKB"> -->
        <span class="kb-logo"><logo /></span>
        <span>NexusKB</span>
        <span v-if="regist">账号注册</span>
      </template>
      <regist-form v-if="regist" @on-regist-success="regist=false" />
      <login-form v-else />
      <p class="kb-login-more">
        <span @click="onRegist">
          <template v-if="regist">已有账号，去登录</template>
          <template v-else>注册账号</template>
        </span>
      </p>
    </n-card>
  </div>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import useUserStore from '@/store/user'
  import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
  import { localRead } from '@/libs/tools'
  import Logo from '@/components/Logo.vue'
  import LoginForm from './login/LoginForm.vue'
  import RegistForm from './login/RegistForm.vue'


  export default defineComponent({
    components: {
      Logo, LoginForm, RegistForm
    },
    setup() {
      const { proxy, ctx } = getCurrentInstance()
      const message = useMessage()
      const router = useRouter()
      const userStore = useUserStore()
      const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE) // light, dark
      const regist = ref(false)
      // 注册账号
      const onRegist = () => {
        regist.value = !regist.value
      }
      return {
        themeType,
        regist, onRegist
      }
    }
  })
</script>
