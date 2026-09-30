package br.com.victorcabral.precos.service;

import br.com.victorcabral.precos.domain.ResumoSemanal;
import br.com.victorcabral.precos.repository.ResumoSemanalRepository;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class PrecoServiceTest {

    @ParameterizedTest
    @ValueSource(strings = {"Paragominas", "PARAGOMINAS", "paragominas"})
    void consulta_gasolina_comum_por_prefixo_com_municipio_normalizado(String municipio) {
        ResumoSemanalRepository repository = mock(ResumoSemanalRepository.class);
        ResumoSemanal resultado = resumo();
        when(repository.buscarMaisRecente(any(), any(), any(), any()))
                .thenReturn(List.of(resultado));

        new PrecoService(repository).precoAtual("pa", municipio, "gasolina comum");

        verify(repository).buscarMaisRecente(
                eq("PA"), eq("PARAGOMINAS"), eq("GASOLINA COMUM%"), any(Pageable.class));
    }

    private ResumoSemanal resumo() {
        ResumoSemanal resumo = mock(ResumoSemanal.class);
        when(resumo.getUf()).thenReturn("PA");
        when(resumo.getMunicipio()).thenReturn("PARAGOMINAS");
        when(resumo.getProduto()).thenReturn("GASOLINA COMUM");
        when(resumo.getSemanaInicio()).thenReturn(LocalDate.of(2026, 9, 20));
        when(resumo.getSemanaFim()).thenReturn(LocalDate.of(2026, 9, 26));
        when(resumo.getPrecoMedio()).thenReturn(new BigDecimal("7.050"));
        when(resumo.getPrecoMinimo()).thenReturn(new BigDecimal("6.800"));
        when(resumo.getPrecoMaximo()).thenReturn(new BigDecimal("7.300"));
        when(resumo.getPostosPesquisados()).thenReturn(10);
        return resumo;
    }
}
