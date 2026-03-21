function formtreeNextRowId(collection) {
  const rows = collection.querySelectorAll("[data-formtree-row-id]");
  let maxId = -1;

  for (const row of rows) {
    const raw = row.getAttribute("data-formtree-row-id");
    const id = Number.parseInt(raw, 10);
    if (!Number.isNaN(id) && id > maxId) {
      maxId = id;
    }
  }

  return String(maxId + 1);
}

function formtreeReplacePlaceholder(root, rowId) {
  for (const el of root.querySelectorAll("[name], [id], [for], [data-formtree-row-id]")) {
    for (const attr of ["name", "id", "for", "data-formtree-row-id"]) {
      const value = el.getAttribute(attr);
      if (value && value.includes("__name__")) {
        el.setAttribute(attr, value.replaceAll("__name__", rowId));
      }
    }
  }
}

document.addEventListener("click", (event) => {
  const deleteButton = event.target.closest("[data-formtree-action='delete']");
  if (deleteButton) {
    const row = deleteButton.closest("[data-formtree-row]");
    if (row) row.remove();
    return;
  }

  const addButton = event.target.closest("[data-formtree-action='add']");
  if (!addButton) return;

  const collection = addButton.closest("[data-formtree-collection]");
  if (!collection) return;

  const template = collection.querySelector("template[data-formtree-prototype]");
  const entries = collection.querySelector("[data-formtree-entries]");
  if (!template || !entries) return;

  const rowId = formtreeNextRowId(collection);
  const fragment = template.content.cloneNode(true);
  const wrapper = document.createElement("div");
  wrapper.appendChild(fragment);

  formtreeReplacePlaceholder(wrapper, rowId);

  while (wrapper.firstChild) {
    entries.appendChild(wrapper.firstChild);
  }
});
