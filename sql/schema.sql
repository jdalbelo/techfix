-- Tabela de Clientes
CREATE TABLE public.clientes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    celular_whatsapp TEXT NOT NULL,
    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT chk_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_celular_whatsapp CHECK (celular_whatsapp ~ '^[0-9]{10,13}$')
);

-- Tabela de Ordens de Serviço
CREATE TABLE public.ordens_servico (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    modelo_computador TEXT NOT NULL,
    problema_relatado TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberto',
    data_abertura TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_cliente FOREIGN KEY (cliente_id) REFERENCES public.clientes (id) ON DELETE CASCADE,
    CONSTRAINT chk_status CHECK (status IN ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue'))
);

-- Tabela de Administradores
CREATE TABLE public.admins (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
