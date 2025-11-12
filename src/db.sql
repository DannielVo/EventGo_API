
CREATE TABLE artists (
	artist_id SERIAL NOT NULL, 
	artist_name VARCHAR NOT NULL, 
	PRIMARY KEY (artist_id)
)

;


CREATE TABLE categories (
	category_id SERIAL NOT NULL, 
	category_name VARCHAR NOT NULL, 
	category_desc VARCHAR, 
	PRIMARY KEY (category_id)
)

;


CREATE TABLE ticket_types (
	ticket_type_id SERIAL NOT NULL, 
	ticket_type_name VARCHAR NOT NULL, 
	ticket_type_desc VARCHAR, 
	PRIMARY KEY (ticket_type_id)
)

;


CREATE TABLE users (
	user_id SERIAL NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	full_name VARCHAR NOT NULL, 
	phone_number VARCHAR, 
	user_image VARCHAR, 
	role VARCHAR NOT NULL, 
	PRIMARY KEY (user_id), 
	UNIQUE (email)
)

;


CREATE TABLE organizers (
	organizer_id SERIAL NOT NULL, 
	user_id INTEGER, 
	company_name VARCHAR NOT NULL, 
	PRIMARY KEY (organizer_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;


CREATE TABLE events (
	event_id SERIAL NOT NULL, 
	organizer_id INTEGER, 
	event_title VARCHAR NOT NULL, 
	event_description VARCHAR, 
	event_category VARCHAR, 
	event_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	event_location VARCHAR NOT NULL, 
	event_status VARCHAR, 
	PRIMARY KEY (event_id), 
	FOREIGN KEY(organizer_id) REFERENCES organizers (organizer_id)
)

;


CREATE TABLE attendees (
	attendee_id SERIAL NOT NULL, 
	event_id INTEGER, 
	user_id INTEGER, 
	check_in_status VARCHAR, 
	check_in_time TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (attendee_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;


CREATE TABLE bookings (
	booking_id SERIAL NOT NULL, 
	user_id INTEGER, 
	event_id INTEGER, 
	booking_date TIMESTAMP WITHOUT TIME ZONE, 
	total_amount FLOAT NOT NULL, 
	payment_status VARCHAR, 
	qr_code VARCHAR NOT NULL, 
	PRIMARY KEY (booking_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id), 
	UNIQUE (qr_code)
)

;


CREATE TABLE discounts (
	discount_id SERIAL NOT NULL, 
	event_id INTEGER, 
	discount_code VARCHAR NOT NULL, 
	discount_value FLOAT NOT NULL, 
	max_usage INTEGER NOT NULL, 
	used_count INTEGER, 
	discount_status VARCHAR, 
	PRIMARY KEY (discount_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id)
)

;


CREATE TABLE event_artist (
	event_id INTEGER NOT NULL, 
	artist_id INTEGER NOT NULL, 
	PRIMARY KEY (event_id, artist_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id), 
	FOREIGN KEY(artist_id) REFERENCES artists (artist_id)
)

;


CREATE TABLE event_category (
	event_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	PRIMARY KEY (event_id, category_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id), 
	FOREIGN KEY(category_id) REFERENCES categories (category_id)
)

;


CREATE TABLE event_media (
	media_id SERIAL NOT NULL, 
	event_id INTEGER, 
	media_url VARCHAR NOT NULL, 
	media_type VARCHAR NOT NULL, 
	PRIMARY KEY (media_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id)
)

;


CREATE TABLE notifications (
	notification_id SERIAL NOT NULL, 
	user_id INTEGER, 
	event_id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	type VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (notification_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id)
)

;


CREATE TABLE reviews (
	review_id SERIAL NOT NULL, 
	event_id INTEGER, 
	user_id INTEGER, 
	review_content VARCHAR NOT NULL, 
	rating INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (review_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;


CREATE TABLE seat_maps (
	seat_map_id SERIAL NOT NULL, 
	event_id INTEGER, 
	row VARCHAR NOT NULL, 
	seat_number VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	PRIMARY KEY (seat_map_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id)
)

;


CREATE TABLE tickets (
	ticket_id SERIAL NOT NULL, 
	ticket_type_id INTEGER, 
	event_id INTEGER, 
	ticket_price FLOAT NOT NULL, 
	ticket_total_quantity INTEGER NOT NULL, 
	ticket_remaining_quantity INTEGER NOT NULL, 
	PRIMARY KEY (ticket_id), 
	FOREIGN KEY(ticket_type_id) REFERENCES ticket_types (ticket_type_id), 
	FOREIGN KEY(event_id) REFERENCES events (event_id)
)

;


CREATE TABLE booking_details (
	booking_detail_id SERIAL NOT NULL, 
	booking_id INTEGER, 
	ticket_id INTEGER, 
	seat_map_id INTEGER, 
	unit_price FLOAT NOT NULL, 
	quantity INTEGER NOT NULL, 
	PRIMARY KEY (booking_detail_id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (booking_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id), 
	FOREIGN KEY(seat_map_id) REFERENCES seat_maps (seat_map_id)
)

;


CREATE TABLE user_discount (
	user_discount_id SERIAL NOT NULL, 
	user_id INTEGER, 
	discount_id INTEGER, 
	booking_id INTEGER, 
	used_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (user_discount_id), 
	CONSTRAINT uq_user_discount UNIQUE (user_id, discount_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(discount_id) REFERENCES discounts (discount_id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (booking_id)
)

;


CREATE TABLE user_tickets (
	user_ticket_id SERIAL NOT NULL, 
	ticket_id INTEGER, 
	user_id INTEGER, 
	qr_code VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	purchase_date TIMESTAMP WITHOUT TIME ZONE, 
	used_date TIMESTAMP WITHOUT TIME ZONE, 
	expire_date TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (user_ticket_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	UNIQUE (qr_code)
)

;

