export async function getData(type) {
    const url = "localhost"
    let return_data = {}
    await fetch(`http://${url}/api/v1/get?type=${type}`, {
        credentials: "include",
        method: "GET",
        mode: "cors",
        headers: {
            "ngrok-skip-browser-warning": "true",
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            if (!response.ok) {
                console.log(response.text())
                throw new Error(response)
            }
            return response.json()
        })
        .then(data => {
            return_data = data
        })
        .catch(err => {
            console.error(err)
        })
    console.log(return_data)
    return return_data
}