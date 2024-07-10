const my_ip = "http://127.0.0.1:5000/"

$(async() => {
  $("select").select2();

  const response = await fetch(my_ip+"data-sets")
  const datasets = await response.json()

  document.getElementById("searchbar_dataset").innerHTML = datasets.map(
      (dataset) => `<option value="${dataset.id}">${dataset.name}</option>`
  );

  $("#my-button").on('click', () => {
      var dataset_id = $('#searchbar_dataset').select2('data')[0].id
      window.sessionStorage.clear();
      window.sessionStorage.setItem('server_url',JSON.stringify({"server_ip":my_ip}))
      window.location.assign(`./mainpage.html?datasetId=${dataset_id}`)
      
  })
})