import { getData } from "./api.js"
import { applyTranslation } from "./translation.js"

const reload_interval = 60000
let last_time_reload = 0
let next_time_reload = 0
let data = {}
let sort_ = "funding"
const exchanges = {
    backpack: true,
    kiloex: true,
    aevo: true,
    paradex: true
  }

function sorted_data() {
  if (sort_ === "funding") {
    data.coins.forEach(coin => {
      if (coin.long.rate < coin.short.rate) {
        let tmp = coin.long
        coin.long = coin.short
        coin.short = tmp
      }
    })
    data['coins'].sort((a, b) => {return b.long.rate-b.short.rate-a.long.rate+a.short.rate})
  } else if (sort_ === "spread") {
    data.coins.forEach(coin => {
      if (coin.long.index_price > coin.short.index_price) {
        let tmp = coin.long
        coin.long = coin.short
        coin.short = tmp
      }
    })
    data.coins.sort((a, b) => {return (b['short']['index_price'] && b['long']['index_price'] ? ((b['short']['index_price']-b['long']['index_price'])*2/(b['long']['index_price']+b['short']['index_price'])*100).toFixed(4) : -1) - (a['short']['index_price'] && a['long']['index_price'] ? ((a['short']['index_price']-a['long']['index_price'])*2/(a['long']['index_price']+a['short']['index_price'])*100).toFixed(4) : -1)})
  }
  return data
}

function show_data() {
  document.querySelector("#main_table tbody").innerHTML = sorted_data().coins.map(coin => {
    if (exchanges[coin.long.exchange]||exchanges[coin.short.exchange]) return createRow(coin)
  }).join("")
}

async function loadData() {
  try {
    data = await getData()
    last_time_reload = Math.floor(new Date().getTime() / 1000)
    next_time_reload = last_time_reload + Math.floor(reload_interval / 1000)
    show_data()
  } catch(err) {
    console.error(err)
  }
}

function createRow(data) {
  const links = {
    backpack: "https://backpack.exchange/trade/#_USD_PERP",
    kiloex: "https://app.kiloex.io/trade?token=#USD",
    aevo: "https://app.aevo.xyz/perpetual/#",
    paradex: "https://app.paradex.trade/trade/#-USD-PERP"
  }
  const time = {
    backpack: 8,
    kiloex: 1,
    aevo: 1,
    paradex: 8
  }
  return `
  <tr>
      <td class="coin-name" rowspan="2">${data['coin']}</td>
      <td class="pair-cell">
          🟢
          <a href="${links[data['long']['exchange']].replace(/#/, data['coin'])}" class="exchange_link"><img src="static/icon/${data['long']['exchange']}.png" width="20px" height="20px"> ${data['long']['exchange']}</a>
          <p style="margin-left: 15px;">${data['long']['index_price'].toFixed(4)}</p>
      </td>
      <td>
          <p>${data['long']['rate'].toFixed(4)}% <small style="margin-left: 5px ;"> ${time[data['long']['exchange']]}h</small> </p>
      </td>
      <td class="coin-name" rowspan="2">${(((data['long']['rate'] * (24 / time[data['long']['exchange']]) ) - (data['short']['rate'] * (24 / time[data['short']['exchange']]) )) * 365).toFixed(4)}%</td>
      <td class="coin-name" rowspan="2"><span class="badge green">${((data['long']['rate'] - data['short']['rate'])).toFixed(4)}%</span></td>
      <td class="coin-name" rowspan="2"><span class="badge green">${data['short']['index_price'] && data['long']['index_price'] ? ((data['short']['index_price']-data['long']['index_price'])*2/(data['long']['index_price']+data['short']['index_price'])*100).toFixed(4) : -1}%</span></td>
  </tr>
  <tr class="second_tr">
      <!-- порожня перша клітинка, бо rowspan у попередньому -->
      <td class="pair-cell">
          🔴
          <a href="${links[data['short']['exchange']].replace(/#/, data['coin'])}" class="exchange_link"><img src="static/icon/${data['short']['exchange']}.png" width="20px" height="20px"> ${data['short']['exchange']}</a>
          <p style="margin-left: 15px;">${data['short']['index_price'].toFixed(4)}</p>
      </td>
      <td style="border-right: 1px solid var(--border);">
          <p>${data['short']['rate'].toFixed(4)}% <small style="margin-left: 5px ;"> ${time[data['short']['exchange']]}h</small> </p>
      </td>
  </tr>
  `
}

document.addEventListener('DOMContentLoaded', () => {
  const btn   = document.getElementById('exchangeDropdownBtn');
  const panel = document.getElementById('exchangeDropdown');
  const reset = document.getElementById('exchangeReset');
  const apply = document.getElementById('exchangeApply');
  const sort_by = document.getElementById("sort-select");

  // відкриваємо / закриваємо панель
  btn.addEventListener('click', e => {
    e.stopPropagation();
    panel.classList.toggle('show');
  });

  // щоб кліки всередині панелі НЕ закривали дропдаун
  panel.addEventListener('click', e => e.stopPropagation());

  // клік поза дропдауном — ховаємо
  document.addEventListener('click', () => panel.classList.remove('show'));

  // Reset: знімаємо всі галочки
  reset.addEventListener('click', () => {
    panel.querySelectorAll('input[type=\"checkbox\"]').forEach(chk => chk.checked = false);
    for (let key of Object.keys(exchanges)) {
      exchanges[key] = true
    }
    show_data()
  });

  // Apply: ховаємо панель (тут можна обробити вибір)
  apply.addEventListener('click', () => {
    panel.classList.remove('show');
    Array.from(document.getElementsByClassName("exchangeCheckbox")).forEach(e => {
      if (!e.checked) {
        exchanges[e.value] = false
      } else {
        exchanges[e.value] = true
      }
    })
    show_data()
  });

  sort_by.addEventListener('change', e => {
    switch (e.target.value) {
      case ("long+short: funding"):
        sort_ = "funding"
        break
      case ("long+short: spread"):
        sort_ = "spread"
        break
    }
    show_data()
  })



  applyTranslation()
  loadData()
  setInterval(() => {
    loadData()
  }, reload_interval)
  setInterval(() => {
    let time_remaining = next_time_reload - Math.round(Date.now()/1000)
    document.getElementById("time").innerHTML = time_remaining + "s"
    if (time_remaining <= 0) {
      document.getElementById("time").classList.add("invisible")
      document.getElementById("loader").classList.remove("invisible")
    } else {
      document.getElementById("time").classList.remove("invisible")
      document.getElementById("loader").classList.add("invisible")
    }
  }, 1000)
});
