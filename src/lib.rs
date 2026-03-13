use once_cell::sync::Lazy;
use pyo3::prelude::*;
use tokenizers::Tokenizer;

static TOKENIZER: Lazy<Tokenizer> = Lazy::new(|| {
    let bytes = include_bytes!("../tokenizer.json");
    Tokenizer::from_bytes(bytes).expect("Failed to load embedded tokenizer.json")
});

/// Count the number of tokens in the given text.
#[pyfunction]
fn count_tokens(text: &str) -> PyResult<usize> {
    let encoding = TOKENIZER
        .encode(text, false)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    Ok(encoding.len())
}

/// Encode text into a list of token IDs.
#[pyfunction]
fn encode(text: &str) -> PyResult<Vec<u32>> {
    let encoding = TOKENIZER
        .encode(text, false)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    Ok(encoding.get_ids().to_vec())
}

/// Decode a list of token IDs back into text.
#[pyfunction]
fn decode(ids: Vec<u32>) -> PyResult<String> {
    TOKENIZER
        .decode(&ids, true)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

/// Encode text and return list of (token_id, token_str) tuples.
#[pyfunction]
fn encode_with_tokens(text: &str) -> PyResult<Vec<(u32, String)>> {
    let encoding = TOKENIZER
        .encode(text, false)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    Ok(encoding
        .get_ids()
        .iter()
        .zip(encoding.get_tokens().iter())
        .map(|(id, tok)| (*id, tok.to_string()))
        .collect())
}

/// Get the vocabulary size of the tokenizer.
#[pyfunction]
fn vocab_size() -> usize {
    TOKENIZER.get_vocab_size(true)
}

/// A Python module implemented in Rust.
#[pymodule]
mod anthropic_tokenizer {
    #[pymodule_export]
    use super::count_tokens;
    #[pymodule_export]
    use super::decode;
    #[pymodule_export]
    use super::encode;
    #[pymodule_export]
    use super::encode_with_tokens;
    #[pymodule_export]
    use super::vocab_size;
}
