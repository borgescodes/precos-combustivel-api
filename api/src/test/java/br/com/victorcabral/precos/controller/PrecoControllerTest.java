package br.com.victorcabral.precos.controller;

import br.com.victorcabral.precos.dto.PrecoResponse;
import br.com.victorcabral.precos.service.PrecoService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.junit.jupiter.api.Test;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class PrecoControllerTest {

    @Test
    void retorna_o_contrato_do_control_vault_para_produto_com_espaco() throws Exception {
        PrecoService service = mock(PrecoService.class);
        when(service.precoAtual(anyString(), anyString(), anyString()))
                .thenReturn(new PrecoResponse(
                        "PA", "PARAGOMINAS", "GASOLINA COMUM",
                        LocalDate.of(2026, 9, 20), LocalDate.of(2026, 9, 26),
                        new BigDecimal("7.050"), new BigDecimal("6.800"),
                        new BigDecimal("7.300"), 10));
        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        MockMvc mvc = MockMvcBuilders.standaloneSetup(new PrecoController(service))
                .setMessageConverters(new MappingJackson2HttpMessageConverter(mapper))
                .build();

        mvc.perform(get("/v1/precos")
                        .queryParam("uf", "PA")
                        .queryParam("municipio", "PARAGOMINAS")
                        .queryParam("produto", "GASOLINA COMUM"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.uf").value("PA"))
                .andExpect(jsonPath("$.municipio").value("PARAGOMINAS"))
                .andExpect(jsonPath("$.produto").value("GASOLINA COMUM"))
                .andExpect(jsonPath("$.semanaInicio").value("2026-09-20"))
                .andExpect(jsonPath("$.semanaFim").value("2026-09-26"))
                .andExpect(jsonPath("$.precoMedio").value(7.05))
                .andExpect(jsonPath("$.precoMinimo").value(6.8))
                .andExpect(jsonPath("$.precoMaximo").value(7.3))
                .andExpect(jsonPath("$.postosPesquisados").value(10));

        verify(service).precoAtual("PA", "PARAGOMINAS", "GASOLINA COMUM");
    }
}
