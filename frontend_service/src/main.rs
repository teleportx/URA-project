use askama::Template;
use axum::{
  extract::State,
  response::{IntoResponse, Response},
  routing::get,
  Router,
};
use sqlx::{postgres::PgPoolOptions, PgPool};
use std::env;
use tower_http::services::ServeDir;

#[derive(Template)]
#[template(path = "index.html")]
struct IndexTemplate;

#[derive(Template)]
#[template(path = "anal.html")]
struct AnalyticsTemplate {
  type1_total: i64,
  type2_total: i64,
  type3_total: i64,
}

#[derive(Template)]
#[template(path = "error.html")]
struct ErrorTemplate;

#[tokio::main]
async fn main() {
  let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
  let db_pool = PgPoolOptions::new()
    .max_connections(5)
    .connect(&database_url)
    .await
    .expect("Failed to connect to Postgres");
  let app = Router::new()
    .route("/", get(index))
    .route("/anal", get(analytics))
    .with_state(db_pool)
    .nest_service(
      "/public",
      ServeDir::new("./public").append_index_html_on_directories(true),
    );
  let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
  axum::serve(listener, app).await.unwrap();
}

async fn index() -> impl IntoResponse {
  IndexTemplate
}

async fn analytics(State(db_pool): State<PgPool>) -> Response {
  if let Some(templ) = get_analytics(db_pool).await {
    return templ.into_response();
  }
  (ErrorTemplate {}).into_response()
}

async fn get_analytics(db_pool: PgPool) -> Option<AnalyticsTemplate> {
  let shit = sqlx::query!("SELECT sret_type, COUNT(*) count FROM sretsession GROUP BY sret_type")
    .fetch_all(&db_pool)
    .await
    .ok()?;
  Some(AnalyticsTemplate {
    type1_total: shit
      .iter()
      .find(|x| x.sret_type == 1)
      .and_then(|x| x.count)
      .unwrap_or(0),
    type2_total: shit
      .iter()
      .find(|x| x.sret_type == 2)
      .and_then(|x| x.count)
      .unwrap_or(0),
    type3_total: shit
      .iter()
      .find(|x| x.sret_type == 3)
      .and_then(|x| x.count)
      .unwrap_or(0),
  })
}
