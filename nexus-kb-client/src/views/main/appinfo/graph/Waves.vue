<style lang="less">
@import url('./node/wave.less');
</style>

<template>
  <div class="waves-wrapper">
    <svg class="waves" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
      viewBox="0 24 150 28" preserveAspectRatio="none" shape-rendering="auto">
      <defs>
        <path id="gentle-wave" d="M-160 44c30 0 58-18 88-18s 58 18 88 18 58-18 88-18 58 18 88 18 v44h-352z" />
      </defs>
      <g class="parallax">
        <use xlink:href="#gentle-wave" x="48" y="0" :fill="themeType.name === 'light' ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.6)'" />
        <use xlink:href="#gentle-wave" x="48" y="3" :fill="themeType.name === 'light' ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.4)'" />
        <use xlink:href="#gentle-wave" x="48" y="5" :fill="themeType.name === 'light' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'" />
        <use xlink:href="#gentle-wave" x="48" y="7" fill="var(--n-color)" />
      </g>
    </svg>
  </div>
</template>
<script>
  import { defineComponent, ref, onMounted, nextTick } from 'vue'
  
  export default defineComponent({
    components: {
    },
    props: {
      themeType: Object
    },
    setup() {
      return {
      }
    }
  })
</script>
