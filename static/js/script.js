window.parseISOString = function parseISOString(s) {
    var b = s.split(/\D+/);
    return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const delBtn = document.querySelector("#delbtn");

const deleteVenue = async () => {
    fetch("http://127.0.0.1:5000/venues/" + delBtn.dataset.id, {
        method: "DELETE",
    }).then((res) => (window.location.href = "/"));
};
