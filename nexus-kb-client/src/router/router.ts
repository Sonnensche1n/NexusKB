import { createRouter, createWebHashHistory } from 'vue-router'
const Login = () => import('../views/Login.vue')
const Main = () => import('../views/Main.vue')
const Chat = () => import('../views/main/Chat.vue')
const Repository = () => import('../views/main/Repository.vue')
const Search = () => import('../views/main/Search.vue')
const RepositoryDetail = () => import('../views/main/repository/Detail.vue')
const Setting = () => import('../views/main/Setting.vue')
const Appinfo = () => import('../views/main/Appinfo.vue')
const AppinfoDetail = () => import('../views/main/appinfo/Detail.vue')
const Docset = () => import('../views/main/Docset.vue')
const DocsetDetail = () => import('../views/main/docset/Detail.vue')

const routes = [
    {
        path: '/login',
        component: Login
    },
    {
        path: '/',
        redirect: '/main/chat',
        children: [
            {
                path: '/main',
                component: Main,
                children: [
                    {
                        path: '/main/chat',
                        component: Chat
                    },
                    {
                        path: '/main/repository',
                        component: Repository
                    },
                    {
                        path: '/main/search',
                        component: Search
                    },
                    {
                        path: '/main/repository/detail',
                        component: RepositoryDetail
                    },
                    {
                        path: '/main/setting',
                        component: Setting
                    },
                    {
                        path: '/main/docset',
                        component: Docset
                    },
                    {
                        path: '/main/docset/detail',
                        component: DocsetDetail
                    },
                    {
                        path: '/main/appinfo',
                        component: Appinfo
                    },
                    {
                        path: '/main/appinfo/detail',
                        component: AppinfoDetail
                    }
                ]
            }
        ]
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})
export default router