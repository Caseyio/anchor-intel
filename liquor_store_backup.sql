--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.18 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: caseyortiz
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO caseyortiz;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: inventory_events; Type: TABLE; Schema: public; Owner: caseyortiz
--

CREATE TABLE public.inventory_events (
    id integer NOT NULL,
    product_id integer NOT NULL,
    change integer NOT NULL,
    reason text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer,
    event_type text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.inventory_events OWNER TO caseyortiz;

--
-- Name: inventory_events_id_seq; Type: SEQUENCE; Schema: public; Owner: caseyortiz
--

CREATE SEQUENCE public.inventory_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventory_events_id_seq OWNER TO caseyortiz;

--
-- Name: inventory_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: caseyortiz
--

ALTER SEQUENCE public.inventory_events_id_seq OWNED BY public.inventory_events.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: caseyortiz
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    sku character varying(100) NOT NULL,
    price numeric(10,2) NOT NULL,
    category character varying(100),
    stock_quantity integer DEFAULT 0,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.products OWNER TO caseyortiz;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: caseyortiz
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO caseyortiz;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: caseyortiz
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: sale_items; Type: TABLE; Schema: public; Owner: caseyortiz
--

CREATE TABLE public.sale_items (
    id integer NOT NULL,
    sale_id integer,
    product_id integer,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL
);


ALTER TABLE public.sale_items OWNER TO caseyortiz;

--
-- Name: sale_items_id_seq; Type: SEQUENCE; Schema: public; Owner: caseyortiz
--

CREATE SEQUENCE public.sale_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sale_items_id_seq OWNER TO caseyortiz;

--
-- Name: sale_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: caseyortiz
--

ALTER SEQUENCE public.sale_items_id_seq OWNED BY public.sale_items.id;


--
-- Name: sales; Type: TABLE; Schema: public; Owner: caseyortiz
--

CREATE TABLE public.sales (
    id integer NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total_amount numeric(10,2) NOT NULL,
    user_id integer,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sales OWNER TO caseyortiz;

--
-- Name: sales_id_seq; Type: SEQUENCE; Schema: public; Owner: caseyortiz
--

CREATE SEQUENCE public.sales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sales_id_seq OWNER TO caseyortiz;

--
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: caseyortiz
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: caseyortiz
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username text NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_role_check CHECK ((role = ANY (ARRAY['admin'::text, 'cashier'::text])))
);


ALTER TABLE public.users OWNER TO caseyortiz;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: caseyortiz
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO caseyortiz;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: caseyortiz
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: inventory_events id; Type: DEFAULT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.inventory_events ALTER COLUMN id SET DEFAULT nextval('public.inventory_events_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: sale_items id; Type: DEFAULT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sale_items ALTER COLUMN id SET DEFAULT nextval('public.sale_items_id_seq'::regclass);


--
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: inventory_events; Type: TABLE DATA; Schema: public; Owner: caseyortiz
--

COPY public.inventory_events (id, product_id, change, reason, "timestamp", user_id, event_type, updated_at) FROM stdin;
1	1	10	Received shipment	2025-06-11 14:39:02.175708	\N	\N	2025-06-12 09:31:43.818753
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: caseyortiz
--

COPY public.products (id, name, sku, price, category, stock_quantity, updated_at) FROM stdin;
2	Espolon Tequila	ESP750	27.99	Spirits	40	2025-06-12 09:29:01.591137
1	Tito's Handmade Vodka	TITO750	22.99	Spirits	23	2025-06-12 09:29:01.591137
\.


--
-- Data for Name: sale_items; Type: TABLE DATA; Schema: public; Owner: caseyortiz
--

COPY public.sale_items (id, sale_id, product_id, quantity, price) FROM stdin;
3	1	1	2	22.99
4	2	1	2	22.99
\.


--
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: caseyortiz
--

COPY public.sales (id, "timestamp", total_amount, user_id, updated_at) FROM stdin;
1	2025-06-11 16:00:16.431112	68.97	\N	2025-06-12 09:31:43.823354
2	2025-06-11 16:51:34.368419	45.98	\N	2025-06-12 09:31:43.823354
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: caseyortiz
--

COPY public.users (id, username, password_hash, role, "timestamp", updated_at) FROM stdin;
1	casey	$2b$12$1AdQm/sBDGbqKH4MF4IWceZNKrDZ.I4W6OJacaj/Sgnneroy5338.	admin	2025-06-12 08:56:58.640777	2025-06-12 09:29:26.732704
\.


--
-- Name: inventory_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: caseyortiz
--

SELECT pg_catalog.setval('public.inventory_events_id_seq', 1, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: caseyortiz
--

SELECT pg_catalog.setval('public.products_id_seq', 2, true);


--
-- Name: sale_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: caseyortiz
--

SELECT pg_catalog.setval('public.sale_items_id_seq', 4, true);


--
-- Name: sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: caseyortiz
--

SELECT pg_catalog.setval('public.sales_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: caseyortiz
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: inventory_events inventory_events_pkey; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.inventory_events
    ADD CONSTRAINT inventory_events_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: products products_sku_key; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);


--
-- Name: sale_items sale_items_pkey; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_pkey PRIMARY KEY (id);


--
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_inventory_events_product_id; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_inventory_events_product_id ON public.inventory_events USING btree (product_id);


--
-- Name: idx_inventory_events_timestamp; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_inventory_events_timestamp ON public.inventory_events USING btree ("timestamp");


--
-- Name: idx_inventory_timestamp; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_inventory_timestamp ON public.inventory_events USING btree ("timestamp");


--
-- Name: idx_products_cat_price; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_products_cat_price ON public.products USING btree (category, price);


--
-- Name: idx_sale_items_product_id; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_sale_items_product_id ON public.sale_items USING btree (product_id);


--
-- Name: idx_sales_timestamp; Type: INDEX; Schema: public; Owner: caseyortiz
--

CREATE INDEX idx_sales_timestamp ON public.sales USING btree ("timestamp");


--
-- Name: inventory_events trigger_update_inventory_events_updated_at; Type: TRIGGER; Schema: public; Owner: caseyortiz
--

CREATE TRIGGER trigger_update_inventory_events_updated_at BEFORE UPDATE ON public.inventory_events FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: products trigger_update_products_updated_at; Type: TRIGGER; Schema: public; Owner: caseyortiz
--

CREATE TRIGGER trigger_update_products_updated_at BEFORE UPDATE ON public.products FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: sales trigger_update_sales_updated_at; Type: TRIGGER; Schema: public; Owner: caseyortiz
--

CREATE TRIGGER trigger_update_sales_updated_at BEFORE UPDATE ON public.sales FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users trigger_update_users_updated_at; Type: TRIGGER; Schema: public; Owner: caseyortiz
--

CREATE TRIGGER trigger_update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: inventory_events inventory_events_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.inventory_events
    ADD CONSTRAINT inventory_events_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: inventory_events inventory_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.inventory_events
    ADD CONSTRAINT inventory_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: sale_items sale_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sale_items sale_items_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id) ON DELETE CASCADE;


--
-- Name: sales sales_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: caseyortiz
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

