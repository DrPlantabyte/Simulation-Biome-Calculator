package net.plantabyte.biomes.test;


import java.lang.reflect.*;
import java.util.Arrays;


public class Tests {
	public static void main(String[] args){
		Arrays.stream(Tests.class.getMethods()).filter(Tests::isTestMethod).forEach((Method test)->{
			System.out.println(test.getName()+"...");
			try {
				test.invoke(null);
				System.out.println("\tSuccess!");
			} catch(InvocationTargetException e) {
				System.out.println("\tFailure!");
				System.out.flush();
				if(e.getCause() != null) {
					e.getCause().printStackTrace(System.err);
				} else {
					e.printStackTrace(System.err);
				}
			} catch(IllegalAccessException e) {
				e.printStackTrace(System.err);
				System.exit(1);
			}
			
		});
	}
	public static void testBiomes(){
		throw new UnsupportedOperationException("Not implemented yet");
	}
	
	private static boolean isTestMethod(Method m){
			return Modifier.isStatic(m.getModifiers())
					&& m.getName().startsWith("test");
		}
}