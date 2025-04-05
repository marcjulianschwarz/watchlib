import "./ListStyle.css";

interface Item {
  name: string;
  date: string;
}

interface ListProps<Item> {
  items: Item[];
  selected?: string;
  onSelect?: (id: string) => void;
}

export function List(props: ListProps<Item>) {
  return (
    <div className="list">
      <div className="list-header">
        <div className="list-header-name">Name</div>
        <div className="list-header-date">Date</div>
      </div>
      <div className="list-body">
        {props.items.map((item) => (
          <div
            key={item.name}
            className={`list-item ${props.selected === item.name ? "selected" : ""}`}
            onClick={() => props.onSelect && props.onSelect(item.name)}
          >
            <div className="list-item-name">{item.name}</div>
            <div className="list-item-date">{item.date}</div>
          </div>
        ))}
      </div>
      <p>{props.selected}</p>
    </div>
  );
}
