<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const overdue_period = ref(null)
const overdue_days = ref(null)
const out = ref(null)

const run = async () => {
  const body = {
    principal: principal.value,
    annual_rate: annual_rate.value,
    months: months.value,
    persist: true,
  }
  if (overdue_period.value != null && overdue_period.value !== '' &&
      overdue_days.value != null && overdue_days.value !== '') {
    body.overdue_period = Number(overdue_period.value)
    body.overdue_days = Number(overdue_days.value)
  }
  out.value = await postJSON('/api/schedule', body)
}
</script>
<template><div class="page">
  <h1>等额本息试算</h1>
  <label>本金 <input v-model.number="principal" /></label>
  <label>年利率% <input v-model.number="annual_rate" /></label>
  <label>月数 <input v-model.number="months" /></label>

  <h2>单期逾期（可选）</h2>
  <div class="overdue">
    <label>逾期期序号 <input v-model.number="overdue_period" type="number" min="1" placeholder="如 1" /></label>
    <label>逾期天数 <input v-model.number="overdue_days" type="number" min="0" placeholder="如 13" /></label>
  </div>
  <p class="hint">留空不计罚息；填写且命中启用规则时，罚息 = 该期月供 × 日罚率 × 超出免罚天数的天数。</p>

  <button @click="run">计算</button>

  <div v-if="out" class="result">
    <p>月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
    <table v-if="out.penalty">
      <tbody>
        <tr><td>原月供</td><td>{{ out.penalty.base_monthly_payment }}</td></tr>
        <tr v-if="out.penalty.applied">
          <td>逾期 第{{ out.penalty.overdue_period }}期 · {{ out.penalty.overdue_days }}天（计罚{{ out.penalty.chargeable_days }}天）</td>
          <td>—</td>
        </tr>
        <tr><td>罚息</td><td>{{ out.penalty.penalty }}</td></tr>
        <tr><td>含罚合计</td><td><strong>{{ out.penalty.payment_with_penalty }}</strong></td></tr>
        <tr v-if="!out.penalty.applied && overdue_period != null"><td colspan="2" class="muted">未命中启用规则或仍在免罚期内，罚息为零。</td></tr>
      </tbody>
    </table>
    <p v-if="out.run_id" class="muted">已写入记录 #{{ out.run_id }}，罚息随记录固化。</p>
  </div>
</div></template>
<style scoped>
.overdue { display:flex; gap:1rem; }
.hint { color:#6b5d48; font-size:.9rem; }
.result { margin-top:1rem; }
.muted { color:#6b5d48; }
</style>
