import { ref, h } from 'vue'
import { NIcon, NEl } from 'naive-ui'

export const renderIconfontIcon = (icon: string, props: any) => {
  return h(NIcon, {
    class: icon,
    ...props
  })
}

export const dialogConfirm = (useDialog: any, dialogProps: any) => {
  const dialog = useDialog.create({
    title: '',
    negativeText: '取消',
    positiveText: '确认',
    negativeButtonProps: {
      'render-icon': () => renderIconfontIcon('iconfont icon-close', {})
    },
    positiveButtonProps: {
      'render-icon': () => renderIconfontIcon('iconfont icon-check', {})
    },
    ...dialogProps,
    onNegativeClick: (e: any) => {
      if ('onNegativeClick' in dialogProps) {
        return dialogProps['onNegativeClick'](e, dialog)
      }
    },
    onPositiveClick: async (e: any) => {
      if ('onPositiveClick' in dialogProps) {
        return dialogProps['onPositiveClick'](e, dialog)
      }
    },
  })
}

export const dialogCreate = (useDialog: any, dialogProps: any, component: any, componentProps: any) => {
  const childVm = ref()
  const dialog = useDialog.create({
    title: '',
    // icon: () => renderIconfontIcon('iconfont icon-plus', { size: '28px' }),
    negativeText: '取消',
    positiveText: '确认',
    negativeButtonProps: {
      'render-icon': () => renderIconfontIcon('iconfont icon-close', {})
    },
    positiveButtonProps: {
      'render-icon': () => renderIconfontIcon('iconfont icon-check', {})
    },
    loading: false,
    ...dialogProps,
    onNegativeClick: (e: any) => {
      if ('onNegativeClick' in dialogProps) {
        return dialogProps['onNegativeClick'](e, dialog)
      }
    },
    onPositiveClick: async (e: any) => {
      let cok = childVm.value.ok
      let data
      let err = false // 是否发生异常
      if (cok && cok instanceof Function) {
        dialog.loading = true
        try {
          data = await cok() // 调用下级组件的 ok 方法
        } catch (error) {
          console.error(error)
          err = true
        }
      }
      if (err) {
        dialog.loading = false
        return false
      }
      if ('onPositiveClick' in dialogProps) {
        let res = dialogProps['onPositiveClick'](data, e, dialog)
        if (res === false) {
          // dialog.loading = false
          return false
        }
      } else {
        dialog.loading = false
      }
    },
    content: () => h(NEl, {
      tag: 'div'
    }, [
      h(component, {
        ref: childVm,
        ...componentProps
      })
    ])
  })
}
/**
 * 将对象转换为select用的数组
 * @param component
 * @returns
 */
export const map2Options = (obj:any, filter: Function) => {
  const options:any[] = []
  Object.keys(obj).map(key => {
    if (filter && !filter(key, obj[key])) {
      return
    }
    let label = obj[key]
    if (typeof label === 'object') {
      label = label.label
    }
    options.push({
      key,
      value: key,
      label,
      disabled: false
    })
  })
  return options
}
