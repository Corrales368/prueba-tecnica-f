--
-- PostgreSQL database dump
--

\restrict rWJ6g09wbWGCavCnti4K5YB0UZk4BJDnIHcQZsPmpepx57ypPjByVj9JjAVCr2C

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asset_readings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.asset_readings (
    code text NOT NULL,
    meter text NOT NULL,
    value numeric NOT NULL,
    read_at timestamp with time zone NOT NULL
);


--
-- Name: assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assets (
    code text NOT NULL,
    name character varying(50) NOT NULL,
    active boolean NOT NULL,
    cost numeric(12,2) NOT NULL,
    location text NOT NULL,
    installed_at timestamp with time zone NOT NULL,
    record_hash character(64) NOT NULL,
    warnings jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rejected_assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rejected_assets (
    code text NOT NULL,
    reasons jsonb NOT NULL,
    raw jsonb NOT NULL,
    rejected_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.runs (
    id integer NOT NULL,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone DEFAULT now() NOT NULL,
    summary jsonb NOT NULL
);


--
-- Name: runs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.runs_id_seq OWNED BY public.runs.id;


--
-- Name: runs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.runs ALTER COLUMN id SET DEFAULT nextval('public.runs_id_seq'::regclass);


--
-- Data for Name: asset_readings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asset_readings (code, meter, value, read_at) FROM stdin;
EQ-001	MED-01	365.0	2026-08-14 05:15:00+00
EQ-005	MED-01	381.3	2026-08-15 10:15:00+00
EQ-003	MED-01	352.9	2026-08-13 06:15:00+00
EQ-006	MED-01	355.0	2026-08-13 09:15:00+00
EQ-007	MED-01	369.2	2026-08-14 11:15:00+00
EQ-006	MED-02	355.0	2026-08-13 09:15:00+00
EQ-009	MED-01	357.1	2026-08-13 12:15:00+00
EQ-011	MED-01	379.2	2026-08-15 07:15:00+00
EQ-011	MED-02	379.2	2026-08-15 07:15:00+00
EQ-013	MED-01	367.1	2026-08-14 08:15:00+00
EQ-015	MED-01	355.0	2026-08-13 09:15:00+00
EQ-012/A	MED-01	444.8	2026-08-14 11:15:00+00
EQ-013	MED-02	367.1	2026-08-14 08:15:00+00
EQ-015	MED-02	355.0	2026-08-13 09:15:00+00
EQ-017	MED-01	383.4	2026-08-15 13:15:00+00
EQ-017	MED-02	383.4	2026-08-15 13:15:00+00
EQ-019	MED-01	371.3	2026-08-14 05:15:00+00
EQ-018	MED-01	357.1	2026-08-13 12:15:00+00
EQ-021	MED-01	352.9	2026-08-13 06:15:00+00
EQ-019	MED-02	371.3	2026-08-14 05:15:00+00
EQ-024	MED-01	355.0	2026-08-13 09:15:00+00
EQ-024	MED-02	355.0	2026-08-13 09:15:00+00
EQ-025	MED-01	369.2	2026-08-14 11:15:00+00
EQ-027	MED-01	357.1	2026-08-13 12:15:00+00
EQ-029	MED-01	385.5	2026-08-15 07:15:00+00
EQ-031/B	MED-01	432.7	2026-08-13 12:15:00+00
EQ-030	MED-01	352.9	2026-08-13 06:15:00+00
EQ-033	MED-01	355.0	2026-08-13 09:15:00+00
EQ-033	MED-02	355.0	2026-08-13 09:15:00+00
EQ-035	MED-01	383.4	2026-08-15 13:15:00+00
EQ-035	MED-02	383.4	2026-08-15 13:15:00+00
EQ-036	MED-01	357.1	2026-08-13 12:15:00+00
EQ-037	MED-01	371.3	2026-08-14 05:15:00+00
EQ-037	MED-02	371.3	2026-08-14 05:15:00+00
EQ-039	MED-01	359.2	2026-08-13 06:15:00+00
EQ-039	MED-02	359.2	2026-08-13 06:15:00+00
EQ-042	MED-01	355.0	2026-08-13 09:15:00+00
EQ-043	MED-01	369.2	2026-08-14 11:15:00+00
EQ-042	MED-02	355.0	2026-08-13 09:15:00+00
EQ-045/C	MED-01	436.9	2026-08-13 09:15:00+00
EQ-047	MED-01	385.5	2026-08-15 07:15:00+00
EQ-048	MED-01	359.2	2026-08-13 06:15:00+00
EQ-048	MED-02	359.2	2026-08-13 06:15:00+00
EQ-049	MED-01	373.4	2026-08-14 08:15:00+00
EQ-051	MED-01	355.0	2026-08-13 09:15:00+00
EQ-051	MED-02	355.0	2026-08-13 09:15:00+00
EQ-053	MED-01	383.4	2026-08-15 13:15:00+00
EQ-054	MED-01	357.1	2026-08-13 12:15:00+00
EQ-053	MED-02	383.4	2026-08-15 13:15:00+00
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assets (code, name, active, cost, location, installed_at, record_hash, warnings, created_at, updated_at) FROM stdin;
EQ-001	Equipo 001	f	1234.56	LOC-B	2026-02-11 06:30:00+00	4d0dc3d1f195a83aa2be39e87ddf6d133c9072a33ad86feb6ab85ab0da009adb	[]	2026-11-08 22:01:01.541736+00	2026-11-08 22:01:01.541736+00
EQ-007	Equipo 007	f	1234.56	LOC-C	2026-08-17 12:30:00+00	8d0c6592e355f19626d98cd95fa85ce47e95a2b7ded2359a4871cd9f44aea44c	[]	2026-11-08 22:01:01.553944+00	2026-11-08 22:01:01.553944+00
EQ-015	Equipo 015	f	890.10	LOC-A	2026-08-16 05:00:00+00	1f056cddaeaa1194c3124911637e9ccebd177c74901a7762b1535e359deb95af	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:01.918634+00	2026-11-08 22:01:01.918634+00
EQ-019	Equipo 019	f	1234.56	LOC-E	2026-04-11 06:30:00+00	2d36c61a677b889c3ce442f8c17714f0e8a800fba499e673f075943ba1c215ae	[]	2026-11-08 22:01:02.280974+00	2026-11-08 22:01:02.280974+00
EQ-027	Equipo 027	f	890.10	LOC-C	2026-04-10 05:00:00+00	62df490db8867ad366b9e888b0216253d9f81e0973c204ca138cde5ed36ca0ac	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.641359+00	2026-11-08 22:01:02.641359+00
EQ-030	Equipo 030	t	1234.56	LOC-A	2026-07-13 05:00:00+00	76df7bca9c434c37aba2b06a5a8aa9a87eae065506b51941d2ea9612198ac108	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.651599+00	2026-11-08 22:01:02.651599+00
EQ-042	Equipo 042	t	1234.56	LOC-C	2026-03-16 05:00:00+00	422dc681663206d436a0cbb59b41635bb8a7c771aeb084af0c36fa15037782c7	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.358703+00	2026-11-08 22:01:03.358703+00
EQ-048	Equipo 048	t	1234.56	LOC-D	2026-01-13 05:00:00+00	2f0087fd6e8c99334f7b7450e926b9ac73372c90f2707d199868fe56d30c8d1f	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.368086+00	2026-11-08 22:01:03.368086+00
EQ-054	Equipo 054	t	1234.56	LOC-E	2026-07-10 05:00:00+00	2bccc1811f2fb2ab160005fc74dd66339b9d30d9b717cd6bcc976dae13403ad9	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.725359+00	2026-11-08 22:01:03.725359+00
EQ-005	Equipo 005	t	12500.00	LOC-A	2026-06-15 10:30:00+00	024b91754784ef22e0a45af29d530f45c46ca3843d464651e627dbae0eb85443	[]	2026-11-08 22:01:01.542007+00	2026-11-08 22:01:01.542007+00
EQ-003	Equipo 003	f	890.10	LOC-D	2026-04-13 05:00:00+00	8290a3ffd45e2610aca0d673d5d7f773b100a1f87f75280880078665cb98b770	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:01.548958+00	2026-11-08 22:01:01.548958+00
EQ-006	Equipo 006	t	1234.56	LOC-B	2026-07-16 05:00:00+00	0a2f9e16fd3d07fd392dac2fa2f585a22480c9c752103d82b5f7dc183fc16fa9	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:01.552966+00	2026-11-08 22:01:01.552966+00
EQ-009	Equipo 009	f	890.10	LOC-E	2026-02-10 05:00:00+00	639a9b5543b300d7df43f42adb809d2498b1500a9b2076fc26193f6ffdf71f84	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:01.908764+00	2026-11-08 22:01:01.908764+00
EQ-011	Equipo 011	t	12500.00	LOC-B	2026-04-12 07:30:00+00	5650509d62e0a2c7085370646cf34af7a76df57d088b40bc6251364b44187f3d	[]	2026-11-08 22:01:01.91371+00	2026-11-08 22:01:01.91371+00
EQ-013	Compresor de tornillo rotativo refrigerado por ace	f	1234.56	LOC-D	2026-06-14 09:30:00+00	ccc5a81c0ba805af89e1208792d986b28a6fa2155d89a506d1a914f69e975457	["name: truncated from 83 to 50 chars"]	2026-11-08 22:01:01.917286+00	2026-11-08 22:01:01.917286+00
EQ-012/A	Equipo 012	t	1234.56	LOC-C	2026-05-13 05:00:00+00	bd2cff83e86e121e06bb1caa92185d1f38c8461615ec85d97dd627c8765c3c47	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:01.916392+00	2026-11-08 22:01:01.916392+00
EQ-017	Equipo 017	t	12500.00	LOC-C	2026-02-18 13:30:00+00	8dcb41762137700a3f3dbed4220b7fe686136d39bf139020f33481e9594f4812	[]	2026-11-08 22:01:02.27245+00	2026-11-08 22:01:02.27245+00
EQ-018	Equipo 018	t	1234.56	LOC-D	2026-03-10 05:00:00+00	a5f272ff8dc6796ca799aacf73c1f8db11f0dd47dadc93180fd02e614abaefdf	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.28033+00	2026-11-08 22:01:02.28033+00
EQ-021	Equipo 021	f	890.10	LOC-B	2026-06-13 05:00:00+00	74cff86dff40145eeac3c4c24c9a76e3cb94595bf84f53d018a810a470cfb903	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.281996+00	2026-11-08 22:01:02.281996+00
EQ-024	Equipo 024	t	1234.56	LOC-E	2026-01-16 05:00:00+00	97cee0ca49d6fcf712e528264de91de5a63540cc647ca5e87859dc4c4980636b	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.285666+00	2026-11-08 22:01:02.285666+00
EQ-025	Equipo 025	f	1234.56	LOC-A	2026-02-17 12:30:00+00	1a036a57984d232d82ccf5e3196a7a12328f91f509e1b86af52358103c8ab4f3	[]	2026-11-08 22:01:02.634608+00	2026-11-08 22:01:02.634608+00
EQ-029	Equipo 029	t	12500.00	LOC-E	2026-06-12 07:30:00+00	5c6d367b2380250845dd42e702f2861f40aa24f1df05d7691c437e62c16d669e	[]	2026-11-08 22:01:02.643948+00	2026-11-08 22:01:02.643948+00
EQ-031/B	Equipo 031	f	1234.56	LOC-B	2026-08-14 09:30:00+00	4455491280c91ef0c416d7f8651bbf1521c2f5c7843c4063ea66dc35885bda7a	[]	2026-11-08 22:01:02.651091+00	2026-11-08 22:01:02.651091+00
EQ-033	Equipo 033	f	890.10	LOC-D	2026-02-16 05:00:00+00	41eb7124db5aea00fb88fd04c4899b833f84656f7c9bc6a5017fb563d81cd3a0	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:02.994416+00	2026-11-08 22:01:02.994416+00
EQ-035	Equipo 035	t	12500.00	LOC-A	2026-04-18 13:30:00+00	42e4ca3bf313ac133fdcbe748f7d18012d62aca078a5f06a1144863b04968b7f	[]	2026-11-08 22:01:02.998436+00	2026-11-08 22:01:02.998436+00
EQ-036	Equipo 036	t	1234.56	LOC-B	2026-05-10 05:00:00+00	bba30e9950dbbdd3677449791ca2943098ed567b7abde62c43ae10642c6e28ac	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.001318+00	2026-11-08 22:01:03.001318+00
EQ-037	Equipo 037	f	1234.56	LOC-C	2026-06-11 06:30:00+00	4f26ad575ca08458f097c79efa0e63882b20a1146d3a0377d73e9c46c2914ad3	[]	2026-11-08 22:01:03.007061+00	2026-11-08 22:01:03.007061+00
EQ-039	Compresor de tornillo rotativo refrigerado por ace	f	890.10	LOC-E	2026-08-13 05:00:00+00	fe2d8788f115a4135d1dbcc4eecc3939ec69c67dfc6f832f7f762c12f626231d	["name: truncated from 83 to 50 chars", "installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.010169+00	2026-11-08 22:01:03.010169+00
EQ-043	Equipo 043	f	1234.56	LOC-D	2026-04-17 12:30:00+00	caaf519b049b50005650c8627fd114e112399bbba5a832b1cf4cfb2169a3b217	[]	2026-11-08 22:01:03.359337+00	2026-11-08 22:01:03.359337+00
EQ-045/C	Equipo 045	f	890.10	LOC-A	2026-06-10 05:00:00+00	5c70af515467e0d6fa2bfe9eaabffd29d1711c7bdc63dd024eb61734c427e726	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.362496+00	2026-11-08 22:01:03.362496+00
EQ-047	Equipo 047	t	12500.00	LOC-C	2026-08-12 07:30:00+00	dd8542999e4e926646a2124c8741d002275a96249cfebe67034b742fa111c915	[]	2026-11-08 22:01:03.366349+00	2026-11-08 22:01:03.366349+00
EQ-049	Equipo 049	f	1234.56	LOC-E	2026-02-14 09:30:00+00	db0bd7f439e94dd1aae09828a0c03f22c2a1dc58463e4f96f2989ce21e1778b7	[]	2026-11-08 22:01:03.717235+00	2026-11-08 22:01:03.717235+00
EQ-051	Equipo 051	f	890.10	LOC-B	2026-04-16 05:00:00+00	7ecc192e455d80cabc7b3c56f9ffff23082a5e018985f4a9c0399200b9a20320	["installed_at: no timezone, assumed -05:00"]	2026-11-08 22:01:03.722016+00	2026-11-08 22:01:03.722016+00
EQ-053	Equipo 053	t	12500.00	LOC-D	2026-06-18 13:30:00+00	df5b717c4c8877066decb5fe832029b884a43a529a17a02bbeb9836933587419	[]	2026-11-08 22:01:03.724459+00	2026-11-08 22:01:03.724459+00
\.


--
-- Data for Name: rejected_assets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rejected_assets (code, reasons, raw, rejected_at) FROM stdin;
EQ-002	["acquisition_cost: missing"]	{"code": "EQ-002", "name": "Equipo 002", "status": "Activo", "updated_at": "2026-08-12T12:00:00-05:00", "installed_at": "2026-03-12T02:30:00-05:00", "parent_location": "LOC-C", "acquisition_cost": null}	2026-11-08 22:01:07.731698+00
EQ-004	["status: missing"]	{"code": "EQ-004", "name": "Equipo 004", "status": null, "updated_at": "2026-08-14T12:00:00-05:00", "installed_at": "2026-05-14T04:30:00-05:00", "parent_location": "LOC-E", "acquisition_cost": 45000.0}	2026-11-08 22:01:07.73692+00
EQ-008	["acquisition_cost: missing"]	{"code": "EQ-008", "name": "Equipo 008", "status": "Activo", "updated_at": "2026-08-18T12:00:00-05:00", "installed_at": "2026-01-18T08:30:00-05:00", "parent_location": "LOC-D", "acquisition_cost": null}	2026-11-08 22:01:08.104571+00
EQ-010	["status: missing"]	{"code": "EQ-010", "name": "Equipo 010", "status": null, "updated_at": "2026-08-20T12:00:00-05:00", "installed_at": "2026-03-11T01:30:00-05:00", "parent_location": "LOC-A", "acquisition_cost": 45000.0}	2026-11-08 22:01:08.108551+00
EQ-014	["acquisition_cost: missing"]	{"code": "EQ-014", "name": "Equipo 014", "status": "Activo", "updated_at": "2026-08-24T12:00:00-05:00", "installed_at": "2026-07-15T05:30:00-05:00", "parent_location": "LOC-E", "acquisition_cost": null}	2026-11-08 22:01:08.112398+00
EQ-016	["status: missing"]	{"code": "EQ-016", "name": "Equipo 016", "status": null, "updated_at": "2026-08-11T12:00:00-05:00", "installed_at": "2026-01-17T07:30:00-05:00", "parent_location": "LOC-B", "acquisition_cost": 45000.0}	2026-11-08 22:01:08.460754+00
EQ-020	["acquisition_cost: missing"]	{"code": "EQ-020", "name": "Equipo 020", "status": "Activo", "updated_at": "2026-08-15T12:00:00-05:00", "installed_at": "2026-05-12T02:30:00-05:00", "parent_location": "LOC-A", "acquisition_cost": null}	2026-11-08 22:01:08.470098+00
EQ-022	["status: missing"]	{"code": "EQ-022", "name": "Equipo 022", "status": null, "updated_at": "2026-08-17T12:00:00-05:00", "installed_at": "2026-07-14T04:30:00-05:00", "parent_location": "LOC-C", "acquisition_cost": 45000.0}	2026-11-08 22:01:08.473325+00
EQ-023	["parent_location: 'LOC-Z' not in catalog"]	{"code": "EQ-023", "name": "Equipo 023", "status": "1", "updated_at": "2026-08-18T12:00:00-05:00", "installed_at": "2026-08-15T05:30:00-05:00", "parent_location": "LOC-Z", "acquisition_cost": "12.500,00"}	2026-11-08 22:01:08.475097+00
EQ-026	["acquisition_cost: missing"]	{"code": "EQ-026", "name": "Compresor de tornillo rotativo refrigerado por aceite de la linea de envasado norte", "status": "Activo", "updated_at": "2026-08-21T12:00:00-05:00", "installed_at": "2026-03-18T08:30:00-05:00", "parent_location": "LOC-B", "acquisition_cost": null}	2026-11-08 22:01:08.829655+00
EQ-028	["status: missing"]	{"code": "EQ-028", "name": "Equipo 028", "status": null, "updated_at": "2026-08-23T12:00:00-05:00", "installed_at": "2026-05-11T01:30:00-05:00", "parent_location": "LOC-D", "acquisition_cost": 45000.0}	2026-11-08 22:01:08.831523+00
EQ-032	["acquisition_cost: missing"]	{"code": "EQ-032", "name": "Equipo 032", "status": "Activo", "updated_at": "2026-08-12T12:00:00-05:00", "installed_at": "2026-01-15T05:30:00-05:00", "parent_location": "LOC-C", "acquisition_cost": null}	2026-11-08 22:01:09.185932+00
EQ-034	["status: missing"]	{"code": "EQ-034", "name": "Equipo 034", "status": null, "updated_at": "2026-08-14T12:00:00-05:00", "installed_at": "2026-03-17T07:30:00-05:00", "parent_location": "LOC-E", "acquisition_cost": 45000.0}	2026-11-08 22:01:09.188669+00
EQ-038	["acquisition_cost: missing"]	{"code": "EQ-038", "name": "Equipo 038", "status": "Activo", "updated_at": "2026-08-18T12:00:00-05:00", "installed_at": "2026-07-12T02:30:00-05:00", "parent_location": "LOC-D", "acquisition_cost": null}	2026-11-08 22:01:09.197727+00
EQ-040	["status: missing"]	{"code": "EQ-040", "name": "Equipo 040", "status": null, "updated_at": "2026-08-20T12:00:00-05:00", "installed_at": "2026-01-14T04:30:00-05:00", "parent_location": "LOC-A", "acquisition_cost": 45000.0}	2026-11-08 22:01:09.547329+00
EQ-041	["parent_location: 'LOC-Z' not in catalog"]	{"code": "EQ-041", "name": "Equipo 041", "status": "1", "updated_at": "2026-08-21T12:00:00-05:00", "installed_at": "2026-02-15T05:30:00-05:00", "parent_location": "LOC-Z", "acquisition_cost": "12.500,00"}	2026-11-08 22:01:09.548044+00
EQ-044	["acquisition_cost: missing"]	{"code": "EQ-044", "name": "Equipo 044", "status": "Activo", "updated_at": "2026-08-24T12:00:00-05:00", "installed_at": "2026-05-18T08:30:00-05:00", "parent_location": "LOC-E", "acquisition_cost": null}	2026-11-08 22:01:09.551615+00
EQ-046	["status: missing"]	{"code": "EQ-046", "name": "Equipo 046", "status": null, "updated_at": "2026-08-11T12:00:00-05:00", "installed_at": "2026-07-11T01:30:00-05:00", "parent_location": "LOC-B", "acquisition_cost": 45000.0}	2026-11-08 22:01:09.555836+00
EQ-050	["acquisition_cost: missing"]	{"code": "EQ-050", "name": "Equipo 050", "status": "Activo", "updated_at": "2026-08-15T12:00:00-05:00", "installed_at": "2026-03-15T05:30:00-05:00", "parent_location": "LOC-A", "acquisition_cost": null}	2026-11-08 22:01:09.910258+00
EQ-052	["status: missing"]	{"code": "EQ-052", "name": "Compresor de tornillo rotativo refrigerado por aceite de la linea de envasado norte", "status": null, "updated_at": "2026-08-17T12:00:00-05:00", "installed_at": "2026-05-17T07:30:00-05:00", "parent_location": "LOC-C", "acquisition_cost": 45000.0}	2026-11-08 22:01:09.914621+00
\.


--
-- Data for Name: runs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.runs (id, started_at, finished_at, summary) FROM stdin;
1	2026-11-08 22:00:59.101535+00	2026-11-08 22:01:03.729195+00	{"read": 57, "failed": 0, "loaded": {"updated": 0, "inserted": 34, "unchanged": 0}, "unique": 54, "seconds": 4.63, "rejected": 20, "duplicates": 3, "transformed": 34, "reasons_by_field": {"status": 9, "parent_location": 2, "acquisition_cost": 9}, "warnings_by_field": {"name": 2, "installed_at": 18}}
2	2026-11-08 22:01:05.656644+00	2026-11-08 22:01:10.273702+00	{"read": 57, "failed": 0, "loaded": {"updated": 0, "inserted": 0, "unchanged": 34}, "unique": 54, "seconds": 4.62, "rejected": 20, "duplicates": 3, "transformed": 34, "reasons_by_field": {"status": 9, "parent_location": 2, "acquisition_cost": 9}, "warnings_by_field": {"name": 2, "installed_at": 18}}
\.


--
-- Name: runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.runs_id_seq', 2, true);


--
-- Name: asset_readings asset_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asset_readings
    ADD CONSTRAINT asset_readings_pkey PRIMARY KEY (code, meter);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (code);


--
-- Name: rejected_assets rejected_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rejected_assets
    ADD CONSTRAINT rejected_assets_pkey PRIMARY KEY (code);


--
-- Name: runs runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_pkey PRIMARY KEY (id);


--
-- Name: asset_readings asset_readings_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asset_readings
    ADD CONSTRAINT asset_readings_code_fkey FOREIGN KEY (code) REFERENCES public.assets(code) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict rWJ6g09wbWGCavCnti4K5YB0UZk4BJDnIHcQZsPmpepx57ypPjByVj9JjAVCr2C

