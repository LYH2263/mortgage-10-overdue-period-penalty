<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const persist = ref(true)
const overduePeriod = ref(null)
const overdueDays = ref(null)
const out = ref(null)
const run = async () => {
  const body = { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: persist.value }
  if (overduePeriod.value && overdueDays.value != null && overdueDays.value !== '') {
    body.overdue = { period: overduePeriod.value, days: overdueDays.value }
  }
  out.value = await postJSON('/api/schedule', body)
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<label>写入记录 <input type="checkbox" v-model="persist" /></label>
<fieldset>
  <legend>单期逾期（可选）</legend>
  <label>逾期期序号 <input type="number" v-model.number="overduePeriod" min="1" placeholder="不填则不计罚息" /></label>
  <label>逾期天数 <input type="number" v-model.number="overdueDays" min="0" /></label>
</fieldset>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
<template v-if="out && out.penalty">
  <p v-if="out.penalty.period">第 {{ out.penalty.period }} 期逾期 {{ out.penalty.days }} 天：
    原月供 {{ out.penalty.base_payment }} · 罚息 {{ out.penalty.penalty }} · 含罚合计 {{ out.penalty.payment_with_penalty }}
    <span v-if="!out.penalty.applied">（无启用规则，未计罚息）</span>
  </p>
  <p v-else>罚息 {{ out.penalty.penalty }} · 含罚合计 {{ out.penalty.payment_with_penalty }}</p>
</template>
</div></template>
