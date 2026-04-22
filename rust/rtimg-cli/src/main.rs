use clap::{Parser, Subcommand};

#[derive(Parser, Debug)]
#[command(name = "rtimg")]
#[command(about = "Bootstrap CLI for RTImg")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    Inspect { path: String },
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Inspect { path } => match std::fs::read(&path) {
            Ok(bytes) => match rtimg_core::parse_header(&bytes) {
                Ok(h) => {
                    println!("RTImg file: {}", path);
                    println!("version: {}.{}", h.version_major, h.version_minor);
                    println!("size: {}x{}", h.width, h.height);
                    println!("channels: {}", h.channels);
                    println!("tiles: {}", h.tile_count);
                }
                Err(err) => {
                    eprintln!("error parsing header: {err}");
                    std::process::exit(1);
                }
            },
            Err(err) => {
                eprintln!("error reading file: {err}");
                std::process::exit(1);
            }
        },
    }
}
