<template>
  <div class="main-content-full-height">
    <!-- 展示模块-暂无数据 -->
    <div class="no-data" v-show="baseNoData">{{ t('noData') }}</div>

    <!-- 展示模块 -->
    <div class="output-area" v-show="baseShow">

      <div class="dialog-user">
        <div class="blank"></div>
        <div class="content">
          <div class="title fxc">
            <img src="@/assets/img/user.png" class="user-img" />
            <el-text>
              {{ t('user') }}
            </el-text>
          </div>
          <el-text class="prompt">
            {{ taskInfo.prompt }}
          </el-text>
        </div>
      </div>

      <div class="dialog-ai">
        <el-text class="title"> OpenManus-AI </el-text>

        <div class="card-row-wrap">
          <div class="card-row-aline">
            <el-timeline class="wp-100">
              <el-timeline-item v-for="(step, index) in taskInfo.stepList" :key="index" :timestamp="step.createdDt"
                placement="top">
                <el-card>
                  <div>
                    <h4 class="color-label mr-10" :class="utils.colorByLabel('step')">
                      {{ t('step') }}
                    </h4>
                    <el-text>{{ step.result }}</el-text>
                  </div>
                  <el-divider />
                  <div v-for="(subStep, subIndex) in step.subList">
                    
    <div v-if="subStep && subStep.result" class="fxsb mtb-10">
      <el-text> {{ subStep.type }} </el-text>
    
                      <el-text class="sub-step-time"> {{ subStep.createdDt }} </el-text>
                    </div>
                    <div>
                      <el-text> {{ typeof subStep.result === 'string' ? subStep.result : JSON.stringify(subStep.result, null, 2) }} </el-text>
                    </div>
                    <el-divider v-if="subIndex != step.subList.length - 1" />
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </div>

      <div class="task-status" v-show="taskInfo != null">
        <el-text class="pr-10">{{ t('taskStatus.name') }}:</el-text>
        <el-text>{{ taskInfo.status }}</el-text>
      </div>

    </div>

  </div>

</template>

<script setup>
import { ref, reactive, inject, computed, onMounted, onUnmounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import { useConfig } from '@/store/config'
import { useI18n } from 'vue-i18n'

const utils = inject('utils')
const config = useConfig()
const { t } = useI18n()

// 视图模式
const viewModel = reactive({
  base: 'show'
})

const baseShow = computed(() => {
  return viewModel.base == 'show'
})

const baseNoData = computed(() => {
  return baseShow && taskInfo.value == null
})

const taskInfo = computed(() => {
  return config.getCurrTask()
})


</script>

<style scoped>
.output-area {
  flex-grow: 1;
}

.dialog-user {
  display: flex;
  justify-content: center;
  align-items: space-between;
  margin-bottom: 16px;
}

.dialog-user .blank {
  flex-grow: 1;
}

.dialog-user .content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: end;
  border-radius: 12px;
  background-color: var(--el-fg-color);
}

.dialog-user .title {
  /** 防止子元素宽度被设置为100%, 子元素的align-self设置除auto和stretch之外的值 */
  align-self: flex-end;
  margin: 6px 16px;
  font-size: 15px;
}

.dialog-user .prompt {
  /** 防止子元素宽度被设置为100%, 子元素的align-self设置除auto和stretch之外的值 */
  align-self: flex-end;
  margin: 0px 16px 6px 16px;
}

.dialog-user .user-img {
  width: 20px;
  height: 20px;
  margin-right: 2px;
  margin-bottom: 4px;
}

.dialog {
  width: 100%;
}

.dialog-ai {
  background-color: var(--el-fg-color);
  border-radius: 12px;
}

.dialog-ai .title {
  margin: 6px 12px;
  font-size: 15px;
}

.task-status {
  align-self: self-start;
  padding-top: 12px;
  padding-bottom: 16px;
}

.sub-step-time {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
