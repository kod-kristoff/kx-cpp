use kx_time::Time;
use kx_rend::Renderer;

pub trait State {
    fn update(dt: Time);
    fn draw(renderer: Box<& dyn Renderer>);
    fn on_enter() {}
    fn on_leave() {}
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
