use serde::Serialize;
use warp::{
    http::StatusCode,
    reply::{json, Json, WithStatus},
};

#[derive(Serialize)]
struct ErrorResponse {
    message: String,
}

pub fn response_error_500(message: String) -> WithStatus<Json> {
    response_error(StatusCode::INTERNAL_SERVER_ERROR, message)
}

pub fn response_error(status: StatusCode, message: String) -> WithStatus<Json> {
    warp::reply::with_status(json(&ErrorResponse { message }), status)
}
