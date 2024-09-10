use web;


CREATE TABLE user_cart (
    cart_item_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

ALTER TABLE products
#DROP COLUMN store;
ADD COLUMN store TEXT NOT NULL;


select * from products;
select * from users;
select * from user_cart;