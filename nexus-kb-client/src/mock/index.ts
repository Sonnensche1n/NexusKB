import Mock from 'mockjs'
import repository from './modules/repository'
import dataset from './modules/dataset'
import chat from './modules/chat'
const { mock } = Mock as any // Mock函数

// mock('/api/knb/repository/my/list', 'post', repository.repositoryList)
// mock('/api/knb/repository', 'post', repository.addRepository)
// mock('/api/knb/repository', 'put', repository.editRepository)
// mock(RegExp('/api/knb/repository/' + '.*'), 'delete', repository.removeRepository)

// mock('/api/knb/dataset/list', 'post', dataset.datasetList)

// mock('/api/knb/chat/list', 'post', chat.chatList)
// mock('/api/knb/chat', 'post', chat.addChat)
// mock('/api/knb/chat', 'put', chat.editChat)
// mock(RegExp('/api/knb/chat/' + '.*'), 'delete', chat.removeChat)

// mock('/api/knb/chat/message/list', 'post', chat.messageList)