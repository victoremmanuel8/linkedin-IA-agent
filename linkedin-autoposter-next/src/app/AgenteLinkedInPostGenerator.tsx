"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";
import styled, { keyframes } from "styled-components";

// URL do backend (ajuste se necessário)
const BACKEND_URL = "http://localhost:5000";

// Animação de loading (spin) para o ícone
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Containers e elementos de layout
const PageWrapper = styled.div`
  min-height: 100vh;
  background: linear-gradient(to bottom right, #1a202c, #2d3748);
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Alinha o conteúdo ao topo */
`;

const Content = styled.div`
  max-width: 768px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Title = styled.h1`
  font-size: 2.25rem;
  font-weight: 700;
  color: #fff;
  text-align: center;
  margin-bottom: 1.5rem;
`;

const Card = styled.div`
  background-color: #2d3748;
  border-radius: 0.5rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.7);
  padding: 1rem;
`;

const CardHeader = styled.div`
  margin-bottom: 1rem;
`;

const CardTitle = styled.h2`
  color: #e2e8f0;
  font-weight: 600;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Input = styled.input.withConfig({
  shouldForwardProp: (prop) => prop !== "hasError",
})<{ hasError: boolean }>`
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  border: 1.5px solid ${({ hasError }) => (hasError ? "#f56565" : "#4a5568")};
  background-color: #1a202c;
  color: #e2e8f0;
  &::placeholder {
    color: #718096;
  }
  &:focus {
    outline: none;
    border-color: ${({ hasError }) => (hasError ? "#f56565" : "#4299e1")};
    box-shadow: 0 0 0 3px
      ${({ hasError }) =>
        hasError ? "rgba(245, 101, 101, 0.5)" : "rgba(66, 153, 225, 0.6)"};
  }
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  min-height: 320px;
  padding: 0.75rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  border: 1.5px solid #4a5568;
  background-color: #1a202c;
  color: #e2e8f0;
  resize: vertical;
  &:disabled {
    opacity: 0.8;
  }
`;

const Button = styled.button`
  width: 100%;
  margin-top: 1rem;
  background-color: #4299e1;
  color: white;
  font-weight: 600;
  padding: 0.75rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  &:hover:not(:disabled) {
    background-color: #3182ce;
  }
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.p`
  color: #f56565;
  font-size: 0.875rem;
  margin-top: 0.25rem;
`;

const LoadingIcon = styled(Loader2)`
  animation: ${spin} 1s linear infinite;
  color: #718096;
`;

const ImgPreview = styled.img`
  width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin-top: 1rem; /* Adiciona um pouco de espaço acima da imagem */
`;

const AgenteLinkedInPostGenerator = () => {
  const [topico, setTopico] = useState("");
  const [resultadosBusca, setResultadosBusca] = useState("");
  const [planoPost, setPlanoPost] = useState("");
  const [promtImage, setPrompt] = useState("");
  const [rascunhoPost, setRascunhoPost] = useState("");
  const [textoRevisado, setTextoRevisado] = useState("");
  const [imagemGeradaUrl, setImagemGeradaUrl] = useState(""); // Descomentado
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const gerarPost = async () => {
    if (!topico.trim()) {
      setError("Por favor, insira um tópico.");
      return;
    }
    setLoading(true);
    setError(null);
    setResultadosBusca("");
    setPlanoPost("");
    setRascunhoPost("");
    setPrompt("");
    setTextoRevisado("");
    setImagemGeradaUrl(""); // Limpa a URL da imagem anterior

    try {
      // 1. Buscar Lançamentos
      const buscaResponse = await fetch(
        `${BACKEND_URL}/buscar?topico=${encodeURIComponent(topico)}`
      );
      if (!buscaResponse.ok)
        throw new Error(`Erro na busca: ${buscaResponse.status}`);
      const buscaData = await buscaResponse.json();
      setResultadosBusca(buscaData.resultado_busca);

      // 2. Planejar Post
      const planoResponse = await fetch(
        `${BACKEND_URL}/planejar?topico=${encodeURIComponent(
          topico
        )}&busca=${encodeURIComponent(buscaData.resultado_busca)}`
      );
      if (!planoResponse.ok)
        throw new Error(`Erro no planejamento: ${planoResponse.status}`);
      const planoData = await planoResponse.json();
      setPlanoPost(planoData.plano_post);

      // 3. Redigir Rascunho
      const rascunhoResponse = await fetch(
        `${BACKEND_URL}/redigir?topico=${encodeURIComponent(
          topico
        )}&plano=${encodeURIComponent(planoData.plano_post)}`
      );
      if (!rascunhoResponse.ok)
        throw new Error(`Erro na redação: ${rascunhoResponse.status}`);
      const rascunhoData = await rascunhoResponse.json();
      setRascunhoPost(rascunhoData.rascunho_post);

      //3.5 prompt da imagem
      const promtImage = await fetch(
        `${BACKEND_URL}/prompt?topico=${encodeURIComponent(
          topico
        )}&plano=${encodeURIComponent(planoData.plano_post)}`
      );
      if (!promtImage.ok)
        throw new Error(`Erro na redação: ${promtImage.status}`);
      const promptData = await promtImage.json();
      setRascunhoPost(promptData.rascunho_post);

      // 4. Gerar Imagem
      // const imagemResponse = await fetch(`${BACKEND_URL}/gerar_imagem`, {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({
      //     rascunho_do_post_imagem: `Crie uma imagem para o seguinte conteúdo de post sobre ${topico}: ${planoData.plano_post}`,
      //   }),
      // });

      // if (!imagemResponse.ok) {
      //   throw new Error(`Erro na geração da imagem: ${imagemResponse.status}`);
      // }

      // const imagemData = await imagemResponse.json();

      // if (imagemData.imagem_url) {
      //   setImagemGeradaUrl(imagemData.imagem_url);
      // } else {
      //   console.warn("Imagem não gerada:", imagemData.text);
      // }

      // 5. Revisar Texto
      const revisaoResponse = await fetch(
        `${BACKEND_URL}/revisar?topico=${encodeURIComponent(
          topico
        )}&rascunho=${encodeURIComponent(rascunhoData.rascunho_post)}`
      );
      if (!revisaoResponse.ok)
        throw new Error(`Erro na revisão: ${revisaoResponse.status}`);
      const revisaoData = await revisaoResponse.json();
      setTextoRevisado(revisaoData.texto_revisado);
    } catch (err: any) {
      setError(err.message || "Ocorreu um erro ao gerar o post.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <Content>
        <Title>Geração de Post para LinkedIn com Agentes</Title>

        <Card>
          <CardHeader>
            <CardTitle>
              <span>Tópico do Post</span>
              {loading && <LoadingIcon size={20} />}
            </CardTitle>
          </CardHeader>
          <Input
            type="text"
            placeholder="Digite o tópico do post (ex: IA no Marketing Digital)"
            value={topico}
            onChange={(e) => setTopico(e.target.value)}
            hasError={!!error}
            disabled={loading}
          />
          {error && <ErrorMessage>{error}</ErrorMessage>}
          <Button onClick={gerarPost} disabled={loading}>
            {loading ? "Gerando Post..." : "Gerar Post"}
          </Button>
        </Card>

        {textoRevisado && (
          <Card>
            <CardHeader>
              <CardTitle>Conteúdo do post</CardTitle>
            </CardHeader>
            <Textarea readOnly value={textoRevisado} />
          </Card>
        )}

        {promtImage && (
          <Card>
            <CardHeader>
              <CardTitle>Conteúdo do prompt</CardTitle>
            </CardHeader>
            <Textarea readOnly value={promtImage} />
          </Card>
        )}
      </Content>
    </PageWrapper>
  );
};

export default AgenteLinkedInPostGenerator;

// {imagemGeradaUrl && (
//   <Card>
//     <CardHeader>
//       <CardTitle>Imagem Gerada</CardTitle>
//     </CardHeader>
//     <ImgPreview src={imagemGeradaUrl} alt="Imagem gerada" />
//   </Card>
// )}
