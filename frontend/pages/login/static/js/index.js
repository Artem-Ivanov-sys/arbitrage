document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementsByTagName("form")[0];
    fetch('http://localhost/api/v1/get/csrf_token', {
        method: 'GET',
        credentials: 'include'
    }).then(resp => {
        return resp.json()
    }).then(data => {
        console.log(data)
    })

  form.addEventListener("submit", e => {
    e.preventDefault()
    const csrftoken = decodeURIComponent(document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1])
    fetch('http://localhost/api/v1/user/login', {
      method: 'POST',
      redirect: 'follow',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken
      },
      body: new URLSearchParams({username: e.target[0].value, password: e.target[1].value})
    }).then(response => {
      if (response.ok)
        return response.json()
      throw new Error("Fetch failed")
    }).then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url
        }
    })
  })
})